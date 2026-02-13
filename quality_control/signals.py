import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from notifications.services import NotificationService
from notifications.models import NotificationType

from .enums import InspectionWorkflowStatus

logger = logging.getLogger(__name__)


@receiver(post_save, sender="quality_control.MaterialArrivalSlip")
def notify_arrival_slip_submitted(sender, instance, **kwargs):
    """When arrival slip is submitted -> notify qc_store group."""
    slip = instance
    if not (slip.is_submitted and slip.status == "SUBMITTED"):
        return

    try:
        entry = slip.po_item_receipt.po_receipt.vehicle_entry
        NotificationService.send_notification_by_auth_group(
            group_name="qc_store",
            title="Arrival Slip Submitted",
            body=f"Arrival slip for {slip.po_item_receipt.item_name} submitted for QC inspection. Entry: {entry.entry_no}",
            notification_type=NotificationType.ARRIVAL_SLIP_SUBMITTED,
            click_action_url=f"/qc",
            company=entry.company,
            extra_data={
                "reference_type": "arrival_slip",
                "reference_id": str(slip.id),
                "vehicle_entry_id": str(entry.id),
                "entry_no": entry.entry_no,
            },
            created_by=slip.submitted_by,
        )
    except Exception as e:
        logger.error(f"Failed to send arrival slip notification: {e}")


@receiver(post_save, sender="quality_control.RawMaterialInspection")
def notify_inspection_workflow(sender, instance, **kwargs):
    """
    Notify target groups based on inspection workflow status:
    - SUBMITTED -> notify qc_chemist
    - QA_CHEMIST_APPROVED -> notify qc_manager
    - QAM_APPROVED -> notify grpo
    - REJECTED -> notify qc_store
    """
    inspection = instance

    # Map workflow status to (target_group, notification_type, title, body)
    status_config = {
        InspectionWorkflowStatus.SUBMITTED: (
            "qc_chemist",
            NotificationType.QC_INSPECTION_SUBMITTED,
            "QC Inspection Awaiting Approval",
            f"Inspection for {inspection.description_of_material} ({inspection.report_no}) is submitted for your approval.",
        ),
        InspectionWorkflowStatus.QA_CHEMIST_APPROVED: (
            "qc_manager",
            NotificationType.QC_CHEMIST_APPROVED,
            "QC Chemist Approved - Awaiting QAM",
            f"Inspection for {inspection.description_of_material} ({inspection.report_no}) approved by QA Chemist. Awaiting your final approval.",
        ),
        InspectionWorkflowStatus.QAM_APPROVED: (
            "grpo",
            NotificationType.QC_QAM_APPROVED,
            "QC Approved - Ready for GRPO",
            f"Inspection for {inspection.description_of_material} ({inspection.report_no}) approved by QAM. Final status: {inspection.get_final_status_display()}.",
        ),
        InspectionWorkflowStatus.REJECTED: (
            "qc_store",
            NotificationType.QC_REJECTED,
            "QC Inspection Rejected",
            f"Inspection for {inspection.description_of_material} ({inspection.report_no}) has been rejected. Remarks: {inspection.remarks or 'N/A'}",
        ),
    }

    workflow = inspection.workflow_status
    if workflow not in status_config:
        return

    try:
        entry = inspection.vehicle_entry
        group_name, ntype, title, body = status_config[workflow]

        NotificationService.send_notification_by_auth_group(
            group_name=group_name,
            title=title,
            body=body,
            notification_type=ntype,
            click_action_url=f"/qc",
            company=entry.company,
            extra_data={
                "reference_type": "inspection",
                "reference_id": str(inspection.id),
                "vehicle_entry_id": str(entry.id),
                "entry_no": entry.entry_no,
                "report_no": inspection.report_no,
                "workflow_status": workflow,
                "final_status": inspection.final_status,
            },
            created_by=inspection.updated_by,
        )
    except Exception as e:
        logger.error(f"Failed to send inspection notification: {e}")
