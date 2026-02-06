from django.db import migrations


def update_group(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    group, created = Group.objects.get_or_create(name='construction_gatein')
    permissions = Permission.objects.filter(content_type__app_label='construction_gatein')
    group.permissions.set(permissions)


def reverse_update(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    try:
        group = Group.objects.get(name='construction_gatein')
        group.permissions.clear()
    except Group.DoesNotExist:
        pass


class Migration(migrations.Migration):

    dependencies = [
        ('construction_gatein', '0006_alter_constructiongateentry_options_and_more'),
    ]

    operations = [
        migrations.RunPython(update_group, reverse_update),
    ]
