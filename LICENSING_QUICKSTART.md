# OpenL2M Licensing - Quick Start Guide

## 🚀 Installation (5 Minutes)

### 1. Add to settings.py

```python
# In INSTALLED_APPS:
'licensing',

# In MIDDLEWARE (at the end):
'licensing.middleware.LicenseCheckMiddleware',
```

### 2. Add to urls.py

```python
# In urlpatterns:
path('licensing/', include('licensing.urls')),
```

### 3. Run Migration

```bash
cd /home/user/openl2m/openl2m
python manage.py migrate licensing
sudo systemctl restart openl2m
```

---

## 🔑 Generate License

### Trial (30 days)
```bash
python manage.py generate_license --type trial --activate
```

### Perpetual (Forever)
```bash
python manage.py generate_license --type perpetual --activate
```

**Save the serial number!** Format: `XXXX-XXXX-XXXX-XXXX`

---

## ✅ Check Status

```bash
python manage.py check_license
```

Or visit: `https://your-server/licensing/status/`

---

## 🔄 Activate License

### Web UI (Easiest)
1. Login as superuser
2. Go to: `/licensing/activate/`
3. Enter serial: `XXXX-XXXX-XXXX-XXXX`
4. Click "Activate"

### Admin Panel
1. Go to: `/admin/licensing/license/`
2. Click license
3. Check "Is active"
4. Save

---

## 📊 What Happens When License Expires?

✅ **Still Works:**
- Login
- View all data
- Browse devices
- Read configurations

❌ **Blocked:**
- Edit interfaces
- Change VLANs
- Modify settings
- Any write operations

**Users see**: "License expired - Read-only mode"

---

## 🛠️ Common Commands

| Action | Command |
|--------|---------|
| Generate trial | `python manage.py generate_license --type trial --activate` |
| Generate perpetual | `python manage.py generate_license --type perpetual --activate` |
| Check status | `python manage.py check_license` |
| Deactivate all | See troubleshooting below |

---

## 🐛 Troubleshooting

### No license found?
```bash
python manage.py generate_license --type trial --activate
```

### Multiple active licenses error?
```bash
python manage.py shell
>>> from licensing.models import License
>>> License.objects.filter(is_active=True).update(is_active=False)
>>> exit()
# Then activate one license
```

### Test expired license (without waiting 30 days)?
```bash
python manage.py shell
>>> from licensing.models import License
>>> from django.utils import timezone
>>> from datetime import timedelta
>>> lic = License.get_active_license()
>>> lic.expiry_date = timezone.now() - timedelta(days=1)
>>> lic.save()
>>> exit()
```

---

## 📝 Quick Examples

### Example 1: First Time Setup
```bash
# After installation
cd /home/user/openl2m/openl2m

# Generate trial license
python manage.py generate_license \
  --type trial \
  --organization "My Company" \
  --email "admin@company.com" \
  --activate

# Output shows serial: 4A2E-9F3B-C7D1-8E56
# Save this serial!

# Check it worked
python manage.py check_license
```

### Example 2: Upgrade Trial to Perpetual
```bash
# Generate perpetual license
python manage.py generate_license --type perpetual --activate
# New serial: EEEE-FFFF-0000-1111

# Old trial is automatically deactivated
# New perpetual is now active
```

### Example 3: Distribute License to Customer
```bash
# 1. Generate license (don't activate yet)
python manage.py generate_license \
  --type perpetual \
  --organization "Customer ABC" \
  --email "admin@customerabc.com"

# Output: Serial = ABCD-1234-EFGH-5678

# 2. Send serial to customer

# 3. Customer activates via web UI at /licensing/activate/
```

---

## 🎯 URLs Reference

| Page | URL |
|------|-----|
| Activate | `/licensing/activate/` |
| Status | `/licensing/status/` |
| Admin | `/admin/licensing/license/` |
| API Check | `/licensing/api/check/` |

---

## 💡 Best Practices

1. **Always save serial numbers** when generating licenses
2. **Use `--activate` flag** for immediate activation during generation
3. **Generate perpetual** for production environments
4. **Generate trial** for demos/testing
5. **Backup database** before major license changes
6. **Test expiry behavior** before going to production

---

## 🔐 License Types Comparison

| Feature | Trial | Perpetual |
|---------|-------|-----------|
| Duration | 30 days | Forever |
| Full Access | ✅ | ✅ |
| Auto-Expiry | ✅ | ❌ |
| Cost | Free/Demo | Paid |
| Production Use | ❌ | ✅ |
| Renewal Required | ✅ | ❌ |

---

## 📞 Need Help?

1. Read full guide: `LICENSING_SETUP.md`
2. Check license status: `python manage.py check_license`
3. View admin panel: `/admin/licensing/license/`
4. Check middleware is enabled in settings.py

---

**Remember**: Serial format is always `XXXX-XXXX-XXXX-XXXX` (16 hex characters with dashes)
