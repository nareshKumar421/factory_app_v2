from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db import transaction
from django.contrib.auth import get_user_model
from ..models import EntryLog, Gate, Visitor, Labour, PersonType

User = get_user_model()


class EntryService:

    @staticmethod
    def create_entry(data, user, request=None):
        # Convert QueryDict to regular dict if needed
        if hasattr(data, 'dict'):
            data = data.dict()
        else:
            data = dict(data)

        visitor_id = data.get("visitor")
        labour_id = data.get("labour")

        print("Creating entry with data:", data)

        # Fetch actual model instances
        visitor_obj = None
        labour_obj = None

        if visitor_id:
            visitor_obj = Visitor.objects.filter(id=visitor_id).first()
            if not visitor_obj:
                raise ValidationError("Visitor not found")
        elif labour_id:
            labour_obj = Labour.objects.filter(id=labour_id).first()
            if not labour_obj:
                raise ValidationError("Labour not found")
        else:
            raise ValidationError("Either visitor or labour is required")

        # Prevent double entry (already inside)
        if visitor_obj:
            existing = EntryLog.objects.filter(
                status="IN",
                visitor=visitor_obj
            ).exists()
        else:
            existing = EntryLog.objects.filter(
                status="IN",
                labour=labour_obj
            ).exists()

        if existing:
            raise ValidationError("Person already inside")

        # Build entry data with proper foreign key handling
        entry_data = {
            "created_by": user,
            "name_snapshot": visitor_obj.name if visitor_obj else labour_obj.name,
            "status": "IN",
        }

        # Handle person_type
        person_type_id = data.get("person_type")
        if person_type_id:
            entry_data["person_type"] = PersonType.objects.get(id=person_type_id)

        # Handle gate_in
        gate_in_id = data.get("gate_in")
        if gate_in_id:
            entry_data["gate_in"] = Gate.objects.get(id=gate_in_id)

        # Handle visitor/labour
        if visitor_obj:
            entry_data["visitor"] = visitor_obj
        if labour_obj:
            entry_data["labour"] = labour_obj

        # Copy optional fields
        optional_fields = ["purpose", "vehicle_no", "remarks"]
        for field in optional_fields:
            if data.get(field):
                entry_data[field] = data[field]

        # Handle approved_by if provided
        if data.get("approved_by"):
            entry_data["approved_by_id"] = data["approved_by"]

        return EntryLog.objects.create(**entry_data)


    @staticmethod
    def exit_entry(entry_id, gate_out_id=None):
        entry = EntryLog.objects.get(id=entry_id)

        if entry.status != "IN":
            raise ValidationError("Already exited")

        entry.status = "OUT"
        entry.exit_time = timezone.now()

        if gate_out_id:
            entry.gate_out = Gate.objects.get(id=gate_out_id)

        entry.save()

        return entry

    @staticmethod
    @transaction.atomic
    def bulk_create_entry(validated_data, user):
        """Create EntryLog records for multiple labours at once.
        Partial success: skips labours already inside, creates the rest."""
        # Resolve shared fields
        gate_in_obj = Gate.objects.get(id=validated_data["gate_in"])
        person_type_obj = PersonType.objects.get(id=validated_data["person_type"])
        approved_by_obj = None
        if validated_data.get("approved_by"):
            approved_by_obj = User.objects.get(id=validated_data["approved_by"])

        labours_data = validated_data["labours"]
        labour_ids = [item["labour_id"] for item in labours_data]

        # Batch fetch: all requested labours
        labour_map = {
            l.id: l
            for l in Labour.objects.filter(
                id__in=labour_ids,
                contractor_id=validated_data["contractor_id"],
                is_active=True,
            )
        }

        # Batch fetch: which of these are already inside
        already_inside_ids = set(
            EntryLog.objects.filter(
                labour_id__in=labour_ids, status="IN"
            ).values_list("labour_id", flat=True)
        )

        results = []
        created_entries = []

        for item in labours_data:
            lid = item["labour_id"]

            if lid not in labour_map:
                results.append({
                    "labour_id": lid,
                    "labour_name": "",
                    "status": "skipped",
                    "reason": "Labour not found or inactive",
                    "entry_log_id": None,
                })
                continue

            labour_obj = labour_map[lid]

            if lid in already_inside_ids:
                results.append({
                    "labour_id": lid,
                    "labour_name": labour_obj.name,
                    "status": "skipped",
                    "reason": "Already inside",
                    "entry_log_id": None,
                })
                continue

            entry = EntryLog.objects.create(
                person_type=person_type_obj,
                labour=labour_obj,
                name_snapshot=labour_obj.name,
                photo_snapshot=labour_obj.photo if labour_obj.photo else None,
                gate_in=gate_in_obj,
                purpose=item.get("purpose", ""),
                vehicle_no=item.get("vehicle_no", ""),
                remarks=item.get("remarks", ""),
                approved_by=approved_by_obj,
                status="IN",
                created_by=user,
            )
            created_entries.append(entry)
            results.append({
                "labour_id": lid,
                "labour_name": labour_obj.name,
                "status": "created",
                "reason": "",
                "entry_log_id": entry.id,
            })

        return {
            "total_requested": len(labours_data),
            "total_created": len(created_entries),
            "total_skipped": len(labours_data) - len(created_entries),
            "results": results,
            "entries": created_entries,
        }

    @staticmethod
    @transaction.atomic
    def bulk_exit_entry(validated_data):
        """Mark exit for multiple labours at once.
        Partial success: skips labours not currently inside, exits the rest."""
        gate_out_obj = Gate.objects.get(id=validated_data["gate_out"])

        labours_data = validated_data["labours"]
        labour_ids = [item["labour_id"] for item in labours_data]

        # Batch fetch: entries currently inside for requested labours
        inside_entries = {
            e.labour_id: e
            for e in EntryLog.objects.filter(
                labour_id__in=labour_ids, status="IN"
            ).select_related("labour")
        }

        results = []
        total_exited = 0
        now = timezone.now()

        for item in labours_data:
            lid = item["labour_id"]

            if lid not in inside_entries:
                results.append({
                    "labour_id": lid,
                    "labour_name": "",
                    "status": "skipped",
                    "reason": "Not currently inside",
                    "entry_log_id": None,
                })
                continue

            entry = inside_entries[lid]
            entry.status = "OUT"
            entry.exit_time = now
            entry.gate_out = gate_out_obj
            entry.save()
            total_exited += 1

            results.append({
                "labour_id": lid,
                "labour_name": entry.labour.name if entry.labour else entry.name_snapshot,
                "status": "exited",
                "reason": "",
                "entry_log_id": entry.id,
            })

        return {
            "total_requested": len(labours_data),
            "total_exited": total_exited,
            "total_skipped": len(labours_data) - total_exited,
            "results": results,
        }
