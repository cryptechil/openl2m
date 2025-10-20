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
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse

from .models import License


def is_superuser(user):
    """Check if user is superuser"""
    return user.is_superuser


@login_required
@user_passes_test(is_superuser)
@require_http_methods(["GET", "POST"])
def activate_license(request):
    """View to activate a license"""

    if request.method == 'POST':
        serial_number = request.POST.get('serial_number', '').strip()

        if not serial_number:
            messages.error(request, "Please enter a serial number.")
            return render(request, 'licensing/activate.html')

        # Verify the serial number
        license_obj = License.verify_serial(serial_number)

        if not license_obj:
            messages.error(
                request,
                f"Invalid serial number: {serial_number}. "
                "Please check the serial and try again."
            )
            return render(request, 'licensing/activate.html')

        # Deactivate all other licenses
        License.objects.filter(is_active=True).update(is_active=False)

        # Activate this license
        license_obj.activate()

        messages.success(
            request,
            f"License activated successfully! "
            f"Type: {license_obj.get_license_type_display()}, "
            f"Status: {license_obj.status}"
        )

        return redirect('licensing:status')

    # GET request - show activation form
    return render(request, 'licensing/activate.html')


@login_required
def license_status(request):
    """View to show current license status"""

    is_valid, message, license_obj = License.check_system_license()

    context = {
        'is_valid': is_valid,
        'message': message,
        'license': license_obj,
    }

    return render(request, 'licensing/status.html', context)


def license_check_api(request):
    """API endpoint to check license status"""

    is_valid, message, license_obj = License.check_system_license()

    data = {
        'valid': is_valid,
        'message': message,
    }

    if license_obj:
        data['license'] = {
            'serial': license_obj.serial_number,
            'type': license_obj.get_license_type_display(),
            'status': license_obj.status,
            'is_expired': license_obj.is_expired,
            'days_remaining': license_obj.days_remaining,
            'organization': license_obj.organization,
        }

    return JsonResponse(data)
