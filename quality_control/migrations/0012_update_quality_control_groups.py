from django.db import migrations


def update_quality_control_groups(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')

    # qc_store group
    qc_store, created = Group.objects.get_or_create(name='qc_store')
    qc_store_permissions = Permission.objects.filter(
        content_type__app_label='quality_control',
        codename__in=[
            'add_materialarrivalslip',
            'change_materialarrivalslip',
            'view_materialarrivalslip',
            'can_submit_arrival_slip',
            'view_rawmaterialinspection',
        ],
    )
    qc_store.permissions.set(qc_store_permissions)

    # qc_chemist group
    qc_chemist, created = Group.objects.get_or_create(name='qc_chemist')
    qc_chemist_permissions = Permission.objects.filter(
        content_type__app_label='quality_control',
        codename__in=[
            'view_materialarrivalslip',
            'add_rawmaterialinspection',
            'change_rawmaterialinspection',
            'view_rawmaterialinspection',
            'can_submit_inspection',
            'can_approve_as_chemist',
        ],
    )
    qc_chemist.permissions.set(qc_chemist_permissions)

    # qc_manager group - gets ALL quality_control permissions
    qc_manager, created = Group.objects.get_or_create(name='qc_manager')
    qc_manager_permissions = Permission.objects.filter(
        content_type__app_label='quality_control',
    )
    qc_manager.permissions.set(qc_manager_permissions)


def reverse_update(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    for name in ['qc_store', 'qc_chemist', 'qc_manager']:
        try:
            group = Group.objects.get(name=name)
            group.permissions.clear()
        except Group.DoesNotExist:
            pass


class Migration(migrations.Migration):

    dependencies = [
        ('quality_control', '0011_alter_materialarrivalslip_options_and_more'),
    ]

    operations = [
        migrations.RunPython(update_quality_control_groups, reverse_update),
    ]
