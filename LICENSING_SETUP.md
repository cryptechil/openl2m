# OpenL2M Licensing System - Installation & Usage Guide

This guide explains how to install and use the licensing system for OpenL2M.

## Table of Contents

1. [Overview](#overview)
2. [Installation](#installation)
3. [Generating Licenses](#generating-licenses)
4. [Activating Licenses](#activating-licenses)
5. [License Types](#license-types)
6. [Testing](#testing)
7. [Troubleshooting](#troubleshooting)

---

## Overview

The licensing system provides two types of licenses:

- **1-Month Trial**: Full access for 30 days from activation
- **Perpetual**: Unlimited access with no expiration

### How It Works

1. **License Generation**: Licenses are generated with unique serial numbers
2. **Activation**: Serial numbers are entered to activate a license
3. **Enforcement**: Middleware checks license validity on every request
4. **Read-Only Mode**: If license is invalid/expired, users can view data but cannot make changes

---

## Installation

### Step 1: Add Licensing App to Settings

Edit `/home/user/openl2m/openl2m/openl2m/settings.py`:

```python
# Find the INSTALLED_APPS section and add 'licensing':

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # ... other apps ...
    'switches',
    'users',
    'counters',
    'notices',
    'licensing',  # <-- ADD THIS LINE
]
```

### Step 2: Add Middleware

In the same `settings.py` file, find the `MIDDLEWARE` section and add the licensing middleware:

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # ... other middleware ...
    'licensing.middleware.LicenseCheckMiddleware',  # <-- ADD THIS LINE (at the end)
]
```

### Step 3: Add URL Routes

Edit `/home/user/openl2m/openl2m/openl2m/urls.py`:

```python
# Add this import at the top
from django.urls import path, include

# In the urlpatterns list, add:
urlpatterns = [
    # ... existing patterns ...
    path('licensing/', include('licensing.urls')),  # <-- ADD THIS LINE
]
```

### Step 4: Run Migrations

```bash
cd /home/user/openl2m/openl2m
python manage.py migrate licensing
```

This creates the database tables for license storage.

### Step 5: Restart the Application

```bash
sudo systemctl restart openl2m
# Or if using gunicorn directly:
# sudo systemctl restart gunicorn
```

---

## Generating Licenses

### Command Line Method (Recommended)

Use the management command to generate licenses:

#### Generate Trial License

```bash
cd /home/user/openl2m/openl2m

# Basic trial license
python manage.py generate_license --type trial

# Trial license with details and auto-activation
python manage.py generate_license \
  --type trial \
  --organization "ACME Corporation" \
  --email "admin@acme.com" \
  --activate
```

#### Generate Perpetual License

```bash
# Basic perpetual license
python manage.py generate_license --type perpetual

# Perpetual license with details and auto-activation
python manage.py generate_license \
  --type perpetual \
  --organization "ACME Corporation" \
  --email "admin@acme.com" \
  --activate
```

**Output Example:**
```
License generated successfully!
Type: 1-Month Trial
Serial Number: 4A2E-9F3B-C7D1-8E56
Organization: ACME Corporation
Email: admin@acme.com

License activated!
Status: Active (30 days remaining)
Expires: 2025-11-20 10:30:45

============================================================
SAVE THIS SERIAL NUMBER:
4A2E-9F3B-C7D1-8E56
============================================================
```

### Python Shell Method

```bash
cd /home/user/openl2m/openl2m
python manage.py shell
```

```python
from licensing.models import LicenseGenerator

# Generate trial license
trial = LicenseGenerator.generate_trial_license(
    organization="ACME Corp",
    contact_email="admin@acme.com"
)
print(f"Trial Serial: {trial.serial_number}")

# Generate perpetual license
perpetual = LicenseGenerator.generate_perpetual_license(
    organization="ACME Corp",
    contact_email="admin@acme.com"
)
print(f"Perpetual Serial: {perpetual.serial_number}")

# Activate a license
trial.activate()
print(f"Status: {trial.status}")
```

---

## Activating Licenses

### Method 1: Web Interface (User-Friendly)

1. **Log in as superuser** to OpenL2M
2. **Navigate to**: `https://your-openl2m-server/licensing/activate/`
3. **Enter the serial number** in format: `XXXX-XXXX-XXXX-XXXX`
4. **Click "Activate License"**

The system will:
- Validate the serial number
- Deactivate any existing license
- Activate the new license
- Show confirmation with license details

### Method 2: Django Admin

1. **Navigate to**: `https://your-openl2m-server/admin/licensing/license/`
2. **Find the license** in the list
3. **Click on it** to edit
4. **Check "Is active"** checkbox
5. **Click "Save"**

**Note**: Only one license can be active at a time. The system will automatically deactivate others.

### Method 3: Management Command

```bash
cd /home/user/openl2m/openl2m
python manage.py shell
```

```python
from licensing.models import License

# Find license by serial
license_obj = License.objects.get(serial_number='4A2E-9F3B-C7D1-8E56')

# Deactivate all licenses first
License.objects.filter(is_active=True).update(is_active=False)

# Activate the license
license_obj.activate()

print(f"Activated: {license_obj.status}")
```

---

## License Types

### 1-Month Trial License

**Features:**
- Full access to all features
- Valid for 30 days from activation
- Expires automatically after 30 days
- Users receive warnings when < 7 days remain
- After expiration: Read-only mode (no changes allowed)

**Use Cases:**
- Evaluation period
- Proof of concept
- Demo environments

**Activation:**
```bash
python manage.py generate_license --type trial --activate
```

### Perpetual License

**Features:**
- Full access to all features
- No expiration date
- Valid indefinitely
- Recommended for production

**Use Cases:**
- Production deployments
- Long-term usage
- Purchased licenses

**Activation:**
```bash
python manage.py generate_license --type perpetual --activate
```

---

## Checking License Status

### Command Line

```bash
cd /home/user/openl2m/openl2m
python manage.py check_license
```

**Output Example:**
```
============================================================
OpenL2M License Status
============================================================

Serial Number: 4A2E-9F3B-C7D1-8E56
Type: 1-Month Trial
Status: Active (23 days remaining)
Organization: ACME Corporation
Activated: 2025-10-20 10:30:45
Expires: 2025-11-20 10:30:45
Days Remaining: 23

License is valid and active.

============================================================
```

### Web Interface

Navigate to: `https://your-openl2m-server/licensing/status/`

Shows:
- Serial number
- License type
- Status (Active/Expired)
- Activation date
- Expiry date (for trials)
- Days remaining
- Visual indicators (green = valid, red = expired)

### API Endpoint

```bash
curl https://your-openl2m-server/licensing/api/check/
```

**Response:**
```json
{
  "valid": true,
  "message": "Trial license active. 23 days remaining.",
  "license": {
    "serial": "4A2E-9F3B-C7D1-8E56",
    "type": "1-Month Trial",
    "status": "Active (23 days remaining)",
    "is_expired": false,
    "days_remaining": 23,
    "organization": "ACME Corporation"
  }
}
```

---

## Testing

### Test Scenario 1: Fresh Installation (No License)

1. Install licensing system
2. Try to make a change (e.g., edit interface)
3. **Expected**: Blocked with "No active license" message
4. **Can do**: View all data (read-only)
5. **Cannot do**: Any POST/PUT/DELETE operations

### Test Scenario 2: Activate Trial License

```bash
# Generate and activate trial
python manage.py generate_license --type trial --activate

# Check status
python manage.py check_license

# Test in web UI
# - Login and try to change interface
# - Should work normally
# - Check /licensing/status/ for details
```

### Test Scenario 3: Expired Trial License

To test expiration without waiting 30 days:

```bash
python manage.py shell
```

```python
from licensing.models import License
from django.utils import timezone
from datetime import timedelta

# Get active license
lic = License.get_active_license()

# Set expiry to yesterday (simulate expired license)
lic.expiry_date = timezone.now() - timedelta(days=1)
lic.save()

# Exit and test
exit()
```

**Expected Behavior:**
- Read operations work (GET requests)
- Write operations blocked (POST/PUT/DELETE)
- Error page shown: "License expired on YYYY-MM-DD"
- Users can view data but cannot make changes

### Test Scenario 4: Perpetual License

```bash
# Generate perpetual license
python manage.py generate_license --type perpetual --activate

# Check status
python manage.py check_license
# Should show: "Perpetual license active"
# No expiry date
```

### Test Scenario 5: Switch Between Licenses

```bash
# Generate two licenses
python manage.py generate_license --type trial
# Save serial: AAAA-BBBB-CCCC-DDDD

python manage.py generate_license --type perpetual
# Save serial: EEEE-FFFF-0000-1111

# Activate first license via web UI
# Go to /licensing/activate/
# Enter AAAA-BBBB-CCCC-DDDD

# Check status - should show trial active

# Activate second license
# Enter EEEE-FFFF-0000-1111

# Check status - should show perpetual active
# First license automatically deactivated
```

---

## Troubleshooting

### Problem: "No active license found" message

**Solution:**
```bash
# Check if any licenses exist
python manage.py shell
>>> from licensing.models import License
>>> License.objects.all()
>>> exit()

# If empty, generate one:
python manage.py generate_license --type trial --activate
```

### Problem: "Only one license can be active" error

**Solution:**
```bash
# Deactivate all licenses first
python manage.py shell
>>> from licensing.models import License
>>> License.objects.filter(is_active=True).update(is_active=False)
>>> exit()

# Then activate the desired license
```

### Problem: Changes blocked even with valid license

**Check:**
1. License is activated: `python manage.py check_license`
2. Middleware is enabled in settings.py
3. Clear browser cache and retry
4. Check logs for errors

### Problem: License expiry date not set for trial

**Solution:**
```bash
python manage.py shell
>>> from licensing.models import License
>>> lic = License.objects.get(serial_number='YOUR-SERIAL')
>>> lic.activate()  # This sets expiry date
>>> exit()
```

### Problem: Cannot access /licensing/activate/ page

**Check:**
1. URL is added to urls.py
2. Application restarted after changes
3. User is logged in as superuser
4. No typos in URL

---

## Admin Interface

Access: `https://your-openl2m-server/admin/licensing/license/`

**Features:**
- View all licenses
- Filter by type, active status
- Search by serial, organization
- Activate/deactivate licenses
- Add notes to licenses
- Color-coded status badges:
  - 🟢 Green: Perpetual/Active
  - 🔵 Blue: Trial active (>7 days)
  - 🟠 Orange: Trial expiring soon (<7 days)
  - 🔴 Red: Expired/Inactive

---

## Security Notes

1. **Serial Numbers are Unique**: Each serial can only be used once
2. **One Active License**: Only one license can be active at a time
3. **Read-Only on Expiry**: System doesn't lock users out, just prevents changes
4. **Superuser Override**: Superusers can always access admin to fix licensing
5. **API Access**: API endpoints also respect licensing (return 403 if invalid)

---

## Migration from Non-Licensed Installation

If you're adding licensing to an existing OpenL2M installation:

```bash
# 1. Backup database first
pg_dump openl2m > openl2m_backup.sql

# 2. Install licensing system (follow Installation section)

# 3. Generate and activate license
python manage.py generate_license --type perpetual --activate

# 4. Test thoroughly in read-only mode first

# 5. Restart application
sudo systemctl restart openl2m
```

---

## License Display in UI (Optional)

To show license status in the navbar, edit `/home/user/openl2m/openl2m/templates/_navbar.html`:

Add before the user menu (around line 91):

```html
<!-- License Status Indicator -->
{% if request.license_obj %}
<li class="nav-item">
  <a class="nav-link" href="{% url 'licensing:status' %}"
     data-bs-toggle="tooltip"
     data-bs-title="{{ request.license_message }}">
    {% if request.license_valid %}
      <i class="fa-solid fa-certificate text-success"></i>
      {% if request.license_obj.days_remaining and request.license_obj.days_remaining < 7 %}
        <span class="badge bg-warning">{{ request.license_obj.days_remaining }}d</span>
      {% endif %}
    {% else %}
      <i class="fa-solid fa-exclamation-triangle text-danger"></i>
      <span class="badge bg-danger">Expired</span>
    {% endif %}
  </a>
</li>
{% endif %}
```

This adds a small icon showing license status with tooltip.

---

## Support

For questions or issues with licensing:
1. Check this documentation
2. Review logs: `/var/log/openl2m/` or application logs
3. Verify database entries: `python manage.py shell`
4. Test with management commands first before using web UI

---

**End of Licensing Setup Guide**
