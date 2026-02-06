from django.db import migrations


def update_group(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    group, created = Group.objects.get_or_create(name='grpo')
    permissions = Permission.objects.filter(content_type__app_label='grpo')
    group.permissions.set(permissions)


def reverse_update(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    try:
        group = Group.objects.get(name='grpo')
        group.permissions.clear()
    except Group.DoesNotExist:
        pass


class Migration(migrations.Migration):

    dependencies = [
        ('grpo', '0004_alter_grpoposting_options'),
    ]

    operations = [
        migrations.RunPython(update_group, reverse_update),
    ]
