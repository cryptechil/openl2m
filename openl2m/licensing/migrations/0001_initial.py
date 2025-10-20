# Generated migration for licensing app

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='License',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('serial_number', models.CharField(help_text='Unique license serial number', max_length=64, unique=True)),
                ('license_type', models.IntegerField(choices=[(1, '1-Month Trial'), (2, 'Perpetual')], default=1, help_text='Type of license')),
                ('organization', models.CharField(blank=True, help_text='Organization name', max_length=255)),
                ('contact_email', models.EmailField(blank=True, help_text='Contact email for license holder', max_length=254)),
                ('activation_date', models.DateTimeField(blank=True, help_text='Date when license was activated', null=True)),
                ('expiry_date', models.DateTimeField(blank=True, help_text='Expiry date for trial licenses (null for perpetual)', null=True)),
                ('is_active', models.BooleanField(default=False, help_text='Whether this license is currently active')),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='When this license record was created')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='Last update timestamp')),
                ('notes', models.TextField(blank=True, help_text='Internal notes about this license')),
            ],
            options={
                'verbose_name': 'License',
                'verbose_name_plural': 'Licenses',
                'ordering': ['-is_active', '-activation_date'],
            },
        ),
    ]
