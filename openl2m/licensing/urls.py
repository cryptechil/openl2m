#
# This file is part of Open Layer 2 Management (OpenL2M).
#
from django.urls import path
from . import views

app_name = 'licensing'

urlpatterns = [
    path('activate/', views.activate_license, name='activate'),
    path('status/', views.license_status, name='status'),
    path('api/check/', views.license_check_api, name='api_check'),
]
