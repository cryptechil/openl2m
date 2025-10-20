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
from django.contrib import admin
from django.utils.html import format_html
from .models import License, LicenseType


@admin.register(License)
class LicenseAdmin(admin.ModelAdmin):
    """Admin interface for License management"""

    list_display = [
        'serial_number',
        'license_type',
        'organization',
        'status_badge',
        'activation_date',
        'expiry_date',
        'days_remaining',
        'is_active',
    ]

    list_filter = [
        'license_type',
        'is_active',
        'activation_date',
    ]

    search_fields = [
        'serial_number',
        'organization',
        'contact_email',
    ]

    readonly_fields = [
        'created_at',
        'updated_at',
        'status_badge',
        'days_remaining',
    ]

    fieldsets = (
        ('License Information', {
            'fields': (
                'serial_number',
                'license_type',
                'is_active',
                'status_badge',
            )
        }),
        ('License Holder', {
            'fields': (
                'organization',
                'contact_email',
            )
        }),
        ('Validity', {
            'fields': (
                'activation_date',
                'expiry_date',
                'days_remaining',
            )
        }),
        ('Metadata', {
            'fields': (
                'notes',
                'created_at',
                'updated_at',
            ),
            'classes': ('collapse',)
        }),
    )

    actions = ['activate_license', 'deactivate_license']

    def status_badge(self, obj):
        """Display status as colored badge"""
        status = obj.status
        if 'Expired' in status or 'Inactive' in status:
            color = 'red'
        elif 'Perpetual' in status:
            color = 'green'
        elif obj.days_remaining and obj.days_remaining < 7:
            color = 'orange'
        else:
            color = 'blue'

        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            status
        )
    status_badge.short_description = 'Status'

    def days_remaining(self, obj):
        """Display days remaining"""
        days = obj.days_remaining
        if days is None:
            return "N/A (Perpetual)"
        return f"{days} days"
    days_remaining.short_description = 'Days Remaining'

    def activate_license(self, request, queryset):
        """Admin action to activate selected license"""
        if queryset.count() > 1:
            self.message_user(request, "You can only activate one license at a time.", level='error')
            return

        license_obj = queryset.first()

        # Deactivate all other licenses
        License.objects.filter(is_active=True).update(is_active=False)

        # Activate selected license
        license_obj.activate()

        self.message_user(request, f"License {license_obj.serial_number} activated successfully.")

    activate_license.short_description = "Activate selected license"

    def deactivate_license(self, request, queryset):
        """Admin action to deactivate selected licenses"""
        count = queryset.count()
        queryset.update(is_active=False)
        self.message_user(request, f"{count} license(s) deactivated successfully.")

    deactivate_license.short_description = "Deactivate selected licenses"

    def save_model(self, request, obj, form, change):
        """Override to handle activation logic"""
        if obj.is_active and not change:
            # New license being activated
            License.objects.filter(is_active=True).update(is_active=False)
            obj.activate()
        else:
            super().save_model(request, obj, form, change)
