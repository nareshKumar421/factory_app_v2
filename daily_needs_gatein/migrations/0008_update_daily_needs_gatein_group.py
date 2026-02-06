from django.db import migrations


def update_group(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    group, created = Group.objects.get_or_create(name='daily_needs_gatein')
    permissions = Permission.objects.filter(content_type__app_label='daily_needs_gatein')
    group.permissions.set(permissions)


def reverse_update(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    try:
        group = Group.objects.get(name='daily_needs_gatein')
        group.permissions.clear()
    except Group.DoesNotExist:
        pass


class Migration(migrations.Migration):

    dependencies = [
        ('daily_needs_gatein', '0007_alter_categorylist_options_and_more'),
    ]

    operations = [
        migrations.RunPython(update_group, reverse_update),
    ]
