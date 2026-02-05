# config/admin.py
"""
Custom Admin Site Configuration for Factory Jivo Wellness

Note: Admin branding (site_header, site_title, index_title) is configured
in settings.py and applied in urls.py
"""

from django.contrib.admin import AdminSite


class FactoryJivoWellnessAdminSite(AdminSite):
    """
    Custom Admin Site for Factory Jivo Wellness Gate Management System
    Reserved for future customizations.
    """
    enable_nav_sidebar = True


# Create custom admin site instance (available for future use)
admin_site = FactoryJivoWellnessAdminSite(name='factory_admin')
