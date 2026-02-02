# config/admin.py
"""
Custom Admin Site Configuration for Factory Jivo Wellness
"""

from django.contrib import admin
from django.contrib.admin import AdminSite


class FactoryJivoWellnessAdminSite(AdminSite):
    """
    Custom Admin Site for Factory Jivo Wellness Gate Management System
    """
    site_header = "Factory Jivo Wellness"
    site_title = "Factory Jivo Wellness Admin"
    index_title = "Gate Management & Quality Control System"

    # Enable view permissions
    enable_nav_sidebar = True


# Create custom admin site instance
admin_site = FactoryJivoWellnessAdminSite(name='factory_admin')
