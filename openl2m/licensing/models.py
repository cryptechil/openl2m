#
# This file is part of Open Layer 2 Management (OpenL2M).
#
# OpenL2M is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License version 3 as published by
# the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details.  You should have received a copy of the GNU General Public
# License along with OpenL2M. If not, see <http://www.gnu.org/licenses/>.
#
import hashlib
import uuid
from datetime import datetime, timedelta

from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError


class LicenseType(models.IntegerChoices):
    """License type choices"""
    TRIAL = 1, "1-Month Trial"
    PERPETUAL = 2, "Perpetual"


class License(models.Model):
    """
    License model to manage OpenL2M licensing.
    Supports trial (1-month) and perpetual licenses.
    """

    # License identification
    serial_number = models.CharField(
        max_length=64,
        unique=True,
        help_text="Unique license serial number"
    )

    # License type
    license_type = models.IntegerField(
        choices=LicenseType.choices,
        default=LicenseType.TRIAL,
        help_text="Type of license"
    )

    # License holder information
    organization = models.CharField(
        max_length=255,
        blank=True,
        help_text="Organization name"
    )

    contact_email = models.EmailField(
        blank=True,
        help_text="Contact email for license holder"
    )

    # License validity
    activation_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date when license was activated"
    )

    expiry_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Expiry date for trial licenses (null for perpetual)"
    )

    # License status
    is_active = models.BooleanField(
        default=False,
        help_text="Whether this license is currently active"
    )

    # Metadata
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When this license record was created"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Last update timestamp"
    )

    notes = models.TextField(
        blank=True,
        help_text="Internal notes about this license"
    )

    class Meta:
        ordering = ['-is_active', '-activation_date']
        verbose_name = "License"
        verbose_name_plural = "Licenses"

    def __str__(self):
        return f"{self.get_license_type_display()} - {self.serial_number} ({self.status})"

    @property
    def status(self):
        """Get current license status"""
        if not self.is_active:
            return "Inactive"
        if self.is_expired:
            return "Expired"
        if self.license_type == LicenseType.PERPETUAL:
            return "Active (Perpetual)"
        days_left = self.days_remaining
        return f"Active ({days_left} days remaining)"

    @property
    def is_expired(self):
        """Check if license is expired"""
        if self.license_type == LicenseType.PERPETUAL:
            return False
        if not self.expiry_date:
            return True
        return timezone.now() > self.expiry_date

    @property
    def is_valid(self):
        """Check if license is valid (active and not expired)"""
        return self.is_active and not self.is_expired

    @property
    def days_remaining(self):
        """Calculate days remaining for trial licenses"""
        if self.license_type == LicenseType.PERPETUAL:
            return None
        if not self.expiry_date:
            return 0
        delta = self.expiry_date - timezone.now()
        return max(0, delta.days)

    def activate(self):
        """Activate this license"""
        self.is_active = True
        self.activation_date = timezone.now()

        # Set expiry date for trial licenses
        if self.license_type == LicenseType.TRIAL:
            self.expiry_date = timezone.now() + timedelta(days=30)
        else:
            self.expiry_date = None

        self.save()

    def deactivate(self):
        """Deactivate this license"""
        self.is_active = False
        self.save()

    def clean(self):
        """Validate license data"""
        super().clean()

        # Ensure only one active license exists
        if self.is_active:
            active_licenses = License.objects.filter(is_active=True)
            if self.pk:
                active_licenses = active_licenses.exclude(pk=self.pk)

            if active_licenses.exists():
                raise ValidationError("Only one license can be active at a time.")

    def save(self, *args, **kwargs):
        """Override save to run validation"""
        self.full_clean()
        super().save(*args, **kwargs)

    @staticmethod
    def verify_serial(serial_number):
        """
        Verify if a serial number is valid.
        Returns the license object if valid, None otherwise.
        """
        try:
            license_obj = License.objects.get(serial_number=serial_number)
            return license_obj
        except License.DoesNotExist:
            return None

    @staticmethod
    def get_active_license():
        """Get the currently active license"""
        try:
            return License.objects.get(is_active=True)
        except License.DoesNotExist:
            return None
        except License.MultipleObjectsReturned:
            # Should not happen due to validation, but handle gracefully
            return License.objects.filter(is_active=True).first()

    @staticmethod
    def check_system_license():
        """
        Check if the system has a valid license.
        Returns (is_valid, message, license_obj)
        """
        license_obj = License.get_active_license()

        if not license_obj:
            return False, "No active license found. Please activate a license.", None

        if license_obj.is_expired:
            return False, f"License expired on {license_obj.expiry_date.strftime('%Y-%m-%d')}.", license_obj

        if license_obj.license_type == LicenseType.TRIAL:
            days = license_obj.days_remaining
            return True, f"Trial license active. {days} days remaining.", license_obj
        else:
            return True, "Perpetual license active.", license_obj


class LicenseGenerator:
    """
    Helper class to generate license serial numbers.
    This should be used server-side only for generating licenses.
    """

    @staticmethod
    def generate_serial(license_type, organization="", custom_data=""):
        """
        Generate a license serial number.
        Format: XXXX-XXXX-XXXX-XXXX
        """
        # Create a unique identifier
        unique_id = str(uuid.uuid4())

        # Combine with license type and organization
        data = f"{license_type}{organization}{custom_data}{unique_id}"

        # Generate hash
        hash_obj = hashlib.sha256(data.encode())
        hex_hash = hash_obj.hexdigest()

        # Take first 16 characters and format
        serial = hex_hash[:16].upper()
        formatted_serial = '-'.join([serial[i:i+4] for i in range(0, 16, 4)])

        return formatted_serial

    @staticmethod
    def generate_trial_license(organization="", contact_email=""):
        """Generate and create a trial license"""
        serial = LicenseGenerator.generate_serial(LicenseType.TRIAL, organization)

        license_obj = License.objects.create(
            serial_number=serial,
            license_type=LicenseType.TRIAL,
            organization=organization,
            contact_email=contact_email,
            is_active=False
        )

        return license_obj

    @staticmethod
    def generate_perpetual_license(organization="", contact_email=""):
        """Generate and create a perpetual license"""
        serial = LicenseGenerator.generate_serial(LicenseType.PERPETUAL, organization)

        license_obj = License.objects.create(
            serial_number=serial,
            license_type=LicenseType.PERPETUAL,
            organization=organization,
            contact_email=contact_email,
            is_active=False
        )

        return license_obj
