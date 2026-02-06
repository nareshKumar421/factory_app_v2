from django.db import migrations


def update_group(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    group, created = Group.objects.get_or_create(name='person_gatein')
    permissions = Permission.objects.filter(content_type__app_label='person_gatein')
    group.permissions.set(permissions)


def reverse_update(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    try:
        group = Group.objects.get(name='person_gatein')
        group.permissions.clear()
    except Group.DoesNotExist:
        pass


class Migration(migrations.Migration):

    dependencies = [
        ('person_gatein', '0004_alter_contractor_options_alter_entrylog_options_and_more'),
    ]

    operations = [
        migrations.RunPython(update_group, reverse_update),
    ]
