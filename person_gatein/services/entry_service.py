from django.utils import timezone
from django.core.exceptions import ValidationError
from ..models import EntryLog, Gate, Visitor, Labour, PersonType


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
