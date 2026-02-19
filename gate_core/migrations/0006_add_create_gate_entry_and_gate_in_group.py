from django.db import migrations


def add_permission_and_group(apps, schema_editor):
    """Add can_create_gate_entry permission and create gate_in group."""
    ContentType = apps.get_model('contenttypes', 'ContentType')
    Permission = apps.get_model('auth', 'Permission')
    Group = apps.get_model('auth', 'Group')

    ct = ContentType.objects.get(app_label='gate_core', model='gatecore')

    # Create the new permission
    create_perm, _ = Permission.objects.get_or_create(
        codename='can_create_gate_entry',
        content_type=ct,
        defaults={'name': 'Can create gate entry'}
    )

    # Get the existing view permission
    view_perm = Permission.objects.get(
        codename='can_view_gate_entry',
        content_type=ct,
    )

    # Create gate_in group with both permissions
    group, _ = Group.objects.get_or_create(name='gate_in')
    group.permissions.add(view_perm, create_perm)

    # Also add the new permission to the existing gate_core group
    try:
        gate_core_group = Group.objects.get(name='gate_core')
        gate_core_group.permissions.add(create_perm)
    except Group.DoesNotExist:
        pass


def remove_permission_and_group(apps, schema_editor):
    """Remove can_create_gate_entry permission and gate_in group."""
    ContentType = apps.get_model('contenttypes', 'ContentType')
    Permission = apps.get_model('auth', 'Permission')
    Group = apps.get_model('auth', 'Group')

    Group.objects.filter(name='gate_in').delete()

    try:
        ct = ContentType.objects.get(app_label='gate_core', model='gatecore')
        Permission.objects.filter(
            codename='can_create_gate_entry', content_type=ct
        ).delete()
    except ContentType.DoesNotExist:
        pass


class Migration(migrations.Migration):

    dependencies = [
        ('gate_core', '0005_gateattachment'),
    ]

    operations = [
        migrations.RunPython(add_permission_and_group, remove_permission_and_group),
    ]
