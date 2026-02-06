from django.db import migrations


def update_group(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    group, created = Group.objects.get_or_create(name='maintenance_gatein')
    permissions = Permission.objects.filter(content_type__app_label='maintenance_gatein')
    group.permissions.set(permissions)


def reverse_update(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    try:
        group = Group.objects.get(name='maintenance_gatein')
        group.permissions.clear()
    except Group.DoesNotExist:
        pass


class Migration(migrations.Migration):

    dependencies = [
        ('maintenance_gatein', '0004_alter_maintenancegateentry_options_and_more'),
    ]

    operations = [
        migrations.RunPython(update_group, reverse_update),
    ]
