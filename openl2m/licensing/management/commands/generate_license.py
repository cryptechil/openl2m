#
# This file is part of Open Layer 2 Management (OpenL2M).
#
# Management command to generate licenses
#
from django.core.management.base import BaseCommand, CommandError
from licensing.models import License, LicenseGenerator, LicenseType


class Command(BaseCommand):
    help = 'Generate a new license for OpenL2M'

    def add_arguments(self, parser):
        parser.add_argument(
            '--type',
            type=str,
            choices=['trial', 'perpetual'],
            required=True,
            help='License type (trial or perpetual)'
        )

        parser.add_argument(
            '--organization',
            type=str,
            default='',
            help='Organization name'
        )

        parser.add_argument(
            '--email',
            type=str,
            default='',
            help='Contact email'
        )

        parser.add_argument(
            '--activate',
            action='store_true',
            help='Activate the license immediately'
        )

    def handle(self, *args, **options):
        license_type = options['type']
        organization = options['organization']
        email = options['email']
        activate = options['activate']

        try:
            # Generate license
            if license_type == 'trial':
                license_obj = LicenseGenerator.generate_trial_license(
                    organization=organization,
                    contact_email=email
                )
            else:
                license_obj = LicenseGenerator.generate_perpetual_license(
                    organization=organization,
                    contact_email=email
                )

            self.stdout.write(self.style.SUCCESS(f'\nLicense generated successfully!'))
            self.stdout.write(f'Type: {license_obj.get_license_type_display()}')
            self.stdout.write(f'Serial Number: {license_obj.serial_number}')
            self.stdout.write(f'Organization: {license_obj.organization or "N/A"}')
            self.stdout.write(f'Email: {license_obj.contact_email or "N/A"}')

            # Activate if requested
            if activate:
                # Deactivate all other licenses
                License.objects.filter(is_active=True).update(is_active=False)

                license_obj.activate()

                self.stdout.write(self.style.SUCCESS(f'\nLicense activated!'))
                self.stdout.write(f'Status: {license_obj.status}')

                if license_obj.license_type == LicenseType.TRIAL:
                    self.stdout.write(f'Expires: {license_obj.expiry_date}')

            else:
                self.stdout.write(self.style.WARNING(
                    f'\nLicense created but NOT activated. '
                    f'Use --activate flag to activate immediately, '
                    f'or activate via admin panel.'
                ))

            self.stdout.write(f'\n' + '='*60)
            self.stdout.write(f'SAVE THIS SERIAL NUMBER:')
            self.stdout.write(self.style.SUCCESS(f'{license_obj.serial_number}'))
            self.stdout.write(f'='*60 + '\n')

        except Exception as e:
            raise CommandError(f'Error generating license: {str(e)}')
