import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from .services import NotificationService
from .models import NotificationType

logger = logging.getLogger(__name__)


def _get_company_users(company, exclude_user=None):
    """
    Get active users in a company who should be notified.
    Excludes the user who triggered the event.
    """
    from company.models import UserCompany

    queryset = UserCompany.objects.filter(
        company=company,
        is_active=True,
    ).select_related("user")

    if exclude_user:
        queryset = queryset.exclude(user=exclude_user)

    return [uc.user for uc in queryset]


@receiver(post_save, sender="driver_management.VehicleEntry")
def notify_gate_entry_created(sender, instance, created, **kwargs):
    """Notify on new gate entry creation."""
    if not created:
        return

    entry = instance
    try:
        users = _get_company_users(entry.company, exclude_user=entry.created_by)
        for user in users:
            NotificationService.send_notification_to_user(
                user=user,
                title="New Gate Entry Created",
                body=f"Gate entry {entry.entry_no} ({entry.get_entry_type_display()}) has been created.",
                notification_type=NotificationType.GATE_ENTRY_CREATED,
                click_action_url=f"/gate-entries/{entry.id}",
                reference_type="vehicle_entry",
                reference_id=entry.id,
                company=entry.company,
                created_by=entry.created_by,
            )
    except Exception as e:
        logger.error(f"Failed to send gate entry notification: {e}")


@receiver(post_save, sender="weighment.Weighment")
def notify_weighment_recorded(sender, instance, created, **kwargs):
    """Notify when weighment is recorded."""
    if not created:
        return

    weighment = instance
    try:
        entry = weighment.vehicle_entry
        users = _get_company_users(entry.company, exclude_user=weighment.created_by)
        for user in users:
            NotificationService.send_notification_to_user(
                user=user,
                title="Weighment Recorded",
                body=f"Weighment recorded for {entry.entry_no}. Net: {weighment.net_weight} kg.",
                notification_type=NotificationType.WEIGHMENT_RECORDED,
                click_action_url=f"/gate-entries/{entry.id}",
                reference_type="vehicle_entry",
                reference_id=entry.id,
                company=entry.company,
                created_by=weighment.created_by,
            )
    except Exception as e:
        logger.error(f"Failed to send weighment notification: {e}")


@receiver(post_save, sender="quality_control.MaterialArrivalSlip")
def notify_arrival_slip_submitted(sender, instance, **kwargs):
    """Notify QC team when an arrival slip is submitted."""
    slip = instance
    if not (slip.is_submitted and slip.status == "SUBMITTED"):
        return

    try:
        entry = slip.po_item_receipt.po_receipt.vehicle_entry
        users = _get_company_users(entry.company, exclude_user=slip.submitted_by)
        for user in users:
            NotificationService.send_notification_to_user(
                user=user,
                title="Arrival Slip Submitted",
                body=f"Arrival slip for {slip.po_item_receipt.item_name} submitted for QC.",
                notification_type=NotificationType.ARRIVAL_SLIP_SUBMITTED,
                click_action_url=f"/gate-entries/{entry.id}/qc",
                reference_type="arrival_slip",
                reference_id=slip.id,
                company=entry.company,
                created_by=slip.submitted_by,
            )
    except Exception as e:
        logger.error(f"Failed to send arrival slip notification: {e}")


@receiver(post_save, sender="quality_control.RawMaterialInspection")
def notify_inspection_workflow(sender, instance, **kwargs):
    """Notify on inspection workflow status changes."""
    from quality_control.enums import InspectionWorkflowStatus

    inspection = instance

    status_map = {
        InspectionWorkflowStatus.SUBMITTED: (
            NotificationType.QC_INSPECTION_SUBMITTED,
            "QC Inspection Submitted",
            f"Inspection for {inspection.description_of_material} submitted for approval.",
        ),
        InspectionWorkflowStatus.QA_CHEMIST_APPROVED: (
            NotificationType.QC_CHEMIST_APPROVED,
            "QC Chemist Approved",
            f"Inspection for {inspection.description_of_material} approved by QA Chemist.",
        ),
        InspectionWorkflowStatus.QAM_APPROVED: (
            NotificationType.QC_QAM_APPROVED,
            "QAM Approved",
            f"Inspection for {inspection.description_of_material} approved by QAM. Status: {inspection.final_status}",
        ),
    }

    workflow = inspection.workflow_status
    if workflow not in status_map:
        return

    try:
        entry = inspection.vehicle_entry
        ntype, title, body = status_map[workflow]
        users = _get_company_users(entry.company)
        for user in users:
            NotificationService.send_notification_to_user(
                user=user,
                title=title,
                body=body,
                notification_type=ntype,
                click_action_url=f"/gate-entries/{entry.id}/qc/{inspection.id}",
                reference_type="inspection",
                reference_id=inspection.id,
                company=entry.company,
            )
    except Exception as e:
        logger.error(f"Failed to send inspection notification: {e}")


@receiver(post_save, sender="grpo.GRPOPosting")
def notify_grpo_status(sender, instance, **kwargs):
    """Notify on GRPO posting success or failure."""
    grpo = instance

    if grpo.status == "POSTED":
        ntype = NotificationType.GRPO_POSTED
        title = "GRPO Posted Successfully"
        body = f"GRPO for PO {grpo.po_receipt.po_number} posted. SAP Doc: {grpo.sap_doc_num}"
    elif grpo.status == "FAILED":
        ntype = NotificationType.GRPO_FAILED
        title = "GRPO Posting Failed"
        body = f"GRPO for PO {grpo.po_receipt.po_number} failed: {grpo.error_message}"
    else:
        return

    try:
        entry = grpo.vehicle_entry
        users = _get_company_users(entry.company)
        for user in users:
            NotificationService.send_notification_to_user(
                user=user,
                title=title,
                body=body,
                notification_type=ntype,
                click_action_url=f"/grpo/{grpo.id}",
                reference_type="grpo_posting",
                reference_id=grpo.id,
                company=entry.company,
                created_by=grpo.posted_by,
            )
    except Exception as e:
        logger.error(f"Failed to send GRPO notification: {e}")
