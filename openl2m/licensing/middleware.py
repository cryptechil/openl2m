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
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.template.response import TemplateResponse

from .models import License


class LicenseCheckMiddleware:
    """
    Middleware to check license validity on every request.
    Blocks write operations if license is invalid.
    """

    # URLs that are always allowed (even without valid license)
    ALLOWED_URLS = [
        '/admin/licensing/',  # License management
        '/admin/login/',      # Admin login
        '/admin/logout/',     # Admin logout
        '/login/',            # User login
        '/logout/',           # User logout
        '/static/',           # Static files
        '/api-auth/',         # API authentication
    ]

    # URL patterns that require valid license for POST/PUT/DELETE
    WRITE_PROTECTED_PATTERNS = [
        '/switches/',
        '/api/',
        '/admin/',
    ]

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if URL is in allowed list
        if self._is_url_allowed(request.path):
            return self.get_response(request)

        # Check license validity
        is_valid, message, license_obj = License.check_system_license()

        # Store license info in request for templates
        request.license_valid = is_valid
        request.license_message = message
        request.license_obj = license_obj

        # For read operations (GET, HEAD, OPTIONS), always allow
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            response = self.get_response(request)
            return response

        # For write operations (POST, PUT, DELETE, PATCH), check license
        if self._is_write_operation(request):
            if not is_valid:
                # Block the operation
                if request.user.is_superuser:
                    # Superuser can access admin to fix license
                    if request.path.startswith('/admin/'):
                        messages.error(
                            request,
                            f"LICENSE INVALID: {message} Please activate a valid license."
                        )
                        return self.get_response(request)

                # For API requests, return JSON error
                if request.path.startswith('/api/'):
                    return HttpResponseForbidden(
                        content=f'{{"error": "License invalid: {message}"}}',
                        content_type='application/json'
                    )

                # For regular users, show error page
                return TemplateResponse(
                    request,
                    'licensing/license_expired.html',
                    {
                        'message': message,
                        'license': license_obj,
                        'is_superuser': request.user.is_superuser,
                    },
                    status=403
                )

        response = self.get_response(request)
        return response

    def _is_url_allowed(self, path):
        """Check if URL is in the allowed list"""
        for allowed_url in self.ALLOWED_URLS:
            if path.startswith(allowed_url):
                return True
        return False

    def _is_write_operation(self, request):
        """Check if this is a write operation that needs license check"""
        if request.method not in ['POST', 'PUT', 'DELETE', 'PATCH']:
            return False

        # Check if path matches write-protected patterns
        for pattern in self.WRITE_PROTECTED_PATTERNS:
            if request.path.startswith(pattern):
                return True

        return False
