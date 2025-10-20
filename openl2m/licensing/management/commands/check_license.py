#
# This file is part of Open Layer 2 Management (OpenL2M).
#
# Management command to check license status
#
from django.core.management.base import BaseCommand
from licensing.models import License


class Command(BaseCommand):
    help = 'Check current license status'

    def handle(self, *args, **options):
        is_valid, message, license_obj = License.check_system_license()

        self.stdout.write('\n' + '='*60)
        self.stdout.write('OpenL2M License Status')
        self.stdout.write('='*60 + '\n')

        if not license_obj:
            self.stdout.write(self.style.ERROR('No active license found!'))
            self.stdout.write('\nTo activate a license, use:')
            self.stdout.write('  python manage.py generate_license --type trial --activate')
            self.stdout.write('  or activate via admin panel at /admin/licensing/')
        else:
            status_style = self.style.SUCCESS if is_valid else self.style.ERROR

            self.stdout.write(f'Serial Number: {license_obj.serial_number}')
            self.stdout.write(f'Type: {license_obj.get_license_type_display()}')
            self.stdout.write(status_style(f'Status: {license_obj.status}'))

            if license_obj.organization:
                self.stdout.write(f'Organization: {license_obj.organization}')

            if license_obj.activation_date:
                self.stdout.write(f'Activated: {license_obj.activation_date}')

            if license_obj.expiry_date:
                self.stdout.write(f'Expires: {license_obj.expiry_date}')

            if license_obj.days_remaining is not None:
                days_style = self.style.WARNING if license_obj.days_remaining < 7 else self.style.SUCCESS
                self.stdout.write(days_style(f'Days Remaining: {license_obj.days_remaining}'))

            self.stdout.write(status_style(f'\n{message}'))

        self.stdout.write('\n' + '='*60 + '\n')
