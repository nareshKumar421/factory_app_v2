from rest_framework import viewsets, status
from rest_framework.decorators import api_view,permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from company.permissions import HasCompanyContext
from django.db.models import Count, Q
from django.utils import timezone
from datetime import datetime, timedelta

from .models import *
from .serializers import *
from .serializers import (
    BulkLabourEntryRequestSerializer,
    BulkLabourExitRequestSerializer,
)
from .services.entry_service import EntryService
from .permissions import (
    CanViewPersonType,
    CanManagePersonType,
    CanViewGate,
    CanManageGate,
    CanManageContractor,
    CanManageVisitor,
    CanManageLabour,
    CanCreateEntry,
    CanViewEntry,
    CanEditEntry,
    CanCancelEntry,
    CanExitEntry,
    CanSearchEntry,
    CanViewDashboard,
)


# -------------------------
# Master ViewSets
# -------------------------
class PersonTypeViewSet(viewsets.ModelViewSet):
    queryset = PersonType.objects.all()
    serializer_class = PersonTypeSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), CanManagePersonType()]
        return [IsAuthenticated(), CanViewPersonType()]


class GateViewSet(viewsets.ModelViewSet):
    queryset = Gate.objects.all()
    serializer_class = GateSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), CanManageGate()]
        return [IsAuthenticated(), CanViewGate()]


class ContractorViewSet(viewsets.ModelViewSet):
    queryset = Contractor.objects.all()
    serializer_class = ContractorSerializer
    permission_classes = [IsAuthenticated, CanManageContractor]


class VisitorViewSet(viewsets.ModelViewSet):
    queryset = Visitor.objects.all()
    serializer_class = VisitorSerializer
    permission_classes = [IsAuthenticated, CanManageVisitor]


class LabourViewSet(viewsets.ModelViewSet):
    queryset = Labour.objects.all()
    serializer_class = LabourSerializer
    permission_classes = [IsAuthenticated, CanManageLabour]

# -------------------------
# Entry APIs
# -------------------------

@api_view(["POST"])
@permission_classes([IsAuthenticated, HasCompanyContext, CanCreateEntry])
def create_entry(request):
    try:
        entry = EntryService.create_entry(request.data, request.user,request=request)
        serializer = EntryLogSerializer(entry)
        return Response(serializer.data)
    except Exception as e:
        return Response({"error": str(e)}, status=400)


@api_view(["POST"])
@permission_classes([IsAuthenticated, HasCompanyContext, CanExitEntry])
def exit_entry(request, pk):
    try:
        gate_out_id = request.data.get("gate_out")
        entry = EntryService.exit_entry(pk, gate_out_id)
        serializer = EntryLogSerializer(entry)
        return Response(serializer.data)
    except Exception as e:
        return Response({"error": str(e)}, status=400)


@api_view(["GET"])
@permission_classes([IsAuthenticated, HasCompanyContext, CanViewEntry])
def inside_list(request):
    entries = EntryLog.objects.filter(status="IN").order_by("-entry_time")
    serializer = EntryLogSerializer(entries, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated, HasCompanyContext, CanViewEntry])
def entries_by_date(request):
    """
    Get all entries filtered by date.

    Query Parameters:
    - date: Single date (YYYY-MM-DD) - returns entries for that specific date
    - start_date: Start date (YYYY-MM-DD) for date range
    - end_date: End date (YYYY-MM-DD) for date range
    - status: Filter by status (IN, OUT, CANCELLED)
    - person_type: Filter by person type ID
    - gate_in: Filter by entry gate ID
    - visitor: Filter by visitor ID
    - labour: Filter by labour ID
    """
    try:
        entries = EntryLog.objects.all()

        # Single date filter
        date = request.query_params.get("date")
        if date:
            try:
                filter_date = datetime.strptime(date, "%Y-%m-%d").date()
                entries = entries.filter(entry_time__date=filter_date)
            except ValueError:
                return Response(
                    {"error": "Invalid date format. Use YYYY-MM-DD"},
                    status=400
                )

        # Date range filter
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")

        if start_date:
            try:
                start = datetime.strptime(start_date, "%Y-%m-%d").date()
                entries = entries.filter(entry_time__date__gte=start)
            except ValueError:
                return Response(
                    {"error": "Invalid start_date format. Use YYYY-MM-DD"},
                    status=400
                )

        if end_date:
            try:
                end = datetime.strptime(end_date, "%Y-%m-%d").date()
                entries = entries.filter(entry_time__date__lte=end)
            except ValueError:
                return Response(
                    {"error": "Invalid end_date format. Use YYYY-MM-DD"},
                    status=400
                )

        # Status filter
        entry_status = request.query_params.get("status")
        if entry_status:
            entries = entries.filter(status=entry_status.upper())

        # Person type filter
        person_type = request.query_params.get("person_type")
        if person_type:
            entries = entries.filter(person_type_id=person_type)
            

        # Gate filter
        gate_in = request.query_params.get("gate_in")
        if gate_in:
            entries = entries.filter(gate_in_id=gate_in)

        # Visitor filter
        visitor = request.query_params.get("visitor")
        if visitor:
            entries = entries.filter(visitor_id=visitor)

        # Labour filter
        labour = request.query_params.get("labour")
        if labour:
            entries = entries.filter(labour_id=labour)

        # Order by entry time (newest first)
        entries = entries.order_by("-entry_time")

        serializer = EntryLogSerializer(entries, many=True)
        return Response({
            "count": entries.count(),
            "results": serializer.data
        })

    except Exception as e:
        return Response({"error": str(e)}, status=400)


@api_view(["GET"])
@permission_classes([IsAuthenticated, HasCompanyContext, CanViewEntry])
def entry_detail(request, pk):
    """
    Get detailed information about a specific entry.
    """
    try:
        entry = get_object_or_404(EntryLog, pk=pk)
        serializer = EntryLogSerializer(entry)

        # Calculate duration
        if entry.status == "IN":
            duration = timezone.now() - entry.entry_time
        elif entry.exit_time:
            duration = entry.exit_time - entry.entry_time
        else:
            duration = None

        response_data = serializer.data
        if duration:
            total_seconds = int(duration.total_seconds())
            hours, remainder = divmod(total_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            response_data["duration"] = {
                "hours": hours,
                "minutes": minutes,
                "seconds": seconds,
                "total_minutes": total_seconds // 60,
                "formatted": f"{hours}h {minutes}m"
            }

        return Response(response_data)
    except Exception as e:
        return Response({"error": str(e)}, status=400)


@api_view(["GET"])
@permission_classes([IsAuthenticated, HasCompanyContext, CanViewEntry])
def visitor_entry_history(request, visitor_id):
    """
    Get entry history for a specific visitor.
    """
    try:
        visitor = get_object_or_404(Visitor, pk=visitor_id)
        entries = EntryLog.objects.filter(visitor=visitor).order_by("-entry_time")

        # Check if currently inside
        is_inside = entries.filter(status="IN").exists()
        current_entry = entries.filter(status="IN").first()

        serializer = EntryLogSerializer(entries, many=True)
        visitor_serializer = VisitorSerializer(visitor)

        return Response({
            "visitor": visitor_serializer.data,
            "is_inside": is_inside,
            "current_entry": EntryLogSerializer(current_entry).data if current_entry else None,
            "total_visits": entries.count(),
            "entries": serializer.data
        })
    except Exception as e:
        return Response({"error": str(e)}, status=400)


@api_view(["GET"])
@permission_classes([IsAuthenticated, HasCompanyContext, CanViewEntry])
def labour_entry_history(request, labour_id):
    """
    Get entry history for a specific labour.
    """
    try:
        labour = get_object_or_404(Labour, pk=labour_id)
        entries = EntryLog.objects.filter(labour=labour).order_by("-entry_time")

        # Check if currently inside
        is_inside = entries.filter(status="IN").exists()
        current_entry = entries.filter(status="IN").first()

        serializer = EntryLogSerializer(entries, many=True)
        labour_serializer = LabourSerializer(labour)

        return Response({
            "labour": labour_serializer.data,
            "is_inside": is_inside,
            "current_entry": EntryLogSerializer(current_entry).data if current_entry else None,
            "total_entries": entries.count(),
            "entries": serializer.data
        })
    except Exception as e:
        return Response({"error": str(e)}, status=400)


@api_view(["GET"])
@permission_classes([IsAuthenticated, HasCompanyContext, CanViewDashboard])
def dashboard_stats(request):
    """
    Get dashboard statistics for gate-in management.
    """
    try:
        today = timezone.now().date()
        now = timezone.now()

        # Current counts
        total_inside = EntryLog.objects.filter(status="IN").count()
        visitors_inside = EntryLog.objects.filter(status="IN", visitor__isnull=False).count()
        labours_inside = EntryLog.objects.filter(status="IN", labour__isnull=False).count()

        # Today's counts
        today_entries = EntryLog.objects.filter(entry_time__date=today)
        today_total = today_entries.count()
        today_visitors = today_entries.filter(visitor__isnull=False).count()
        today_labours = today_entries.filter(labour__isnull=False).count()
        today_exits = today_entries.filter(status="OUT").count()

        # Gate-wise current count
        gate_stats = Gate.objects.filter(is_active=True).annotate(
            inside_count=Count('entries_in', filter=Q(entries_in__status="IN"))
        ).values('id', 'name', 'inside_count')

        # Person type wise count
        person_type_stats = PersonType.objects.filter(is_active=True).annotate(
            inside_count=Count('entrylog', filter=Q(entrylog__status="IN")),
            today_count=Count('entrylog', filter=Q(entrylog__entry_time__date=today))
        ).values('id', 'name', 'inside_count', 'today_count')

        # Entries exceeding 8 hours
        eight_hours_ago = now - timedelta(hours=8)
        long_duration_entries = EntryLog.objects.filter(
            status="IN",
            entry_time__lt=eight_hours_ago
        ).count()

        # Recent entries (last 10)
        recent_entries = EntryLog.objects.order_by("-entry_time")[:10]
        recent_serializer = EntryLogSerializer(recent_entries, many=True)

        return Response({
            "current": {
                "total_inside": total_inside,
                "visitors_inside": visitors_inside,
                "labours_inside": labours_inside,
                "long_duration_count": long_duration_entries
            },
            "today": {
                "total_entries": today_total,
                "visitors": today_visitors,
                "labours": today_labours,
                "exits": today_exits
            },
            "gate_wise": list(gate_stats),
            "person_type_wise": list(person_type_stats),
            "recent_entries": recent_serializer.data
        })
    except Exception as e:
        return Response({"error": str(e)}, status=400)


@api_view(["POST"])
@permission_classes([IsAuthenticated, HasCompanyContext, CanCancelEntry])
def cancel_entry(request, pk):
    """
    Cancel an entry (mark as CANCELLED).
    Only entries with status 'IN' can be cancelled.
    """
    try:
        entry = get_object_or_404(EntryLog, pk=pk)

        if entry.status != "IN":
            return Response(
                {"error": "Only entries with status 'IN' can be cancelled"},
                status=400
            )

        reason = request.data.get("reason", "")

        entry.status = "CANCELLED"
        entry.remarks = f"{entry.remarks or ''}\nCancelled: {reason}".strip()
        entry.save()

        serializer = EntryLogSerializer(entry)
        return Response(serializer.data)
    except Exception as e:
        return Response({"error": str(e)}, status=400)


@api_view(["PATCH"])
@permission_classes([IsAuthenticated, HasCompanyContext, CanEditEntry])
def update_entry(request, pk):
    """
    Update entry details (purpose, remarks, vehicle_no, approved_by).
    """
    try:
        entry = get_object_or_404(EntryLog, pk=pk)

        # Only allow updating specific fields
        allowed_fields = ["purpose", "remarks", "vehicle_no", "approved_by"]

        for field in allowed_fields:
            if field in request.data:
                setattr(entry, field, request.data[field])

        entry.save()

        serializer = EntryLogSerializer(entry)
        return Response(serializer.data)
    except Exception as e:
        return Response({"error": str(e)}, status=400)


@api_view(["GET"])
@permission_classes([IsAuthenticated, HasCompanyContext, CanSearchEntry])
def search_entries(request):
    """
    Search entries by name, vehicle number, or purpose.

    Query Parameters:
    - q: Search query (searches in name_snapshot, vehicle_no, purpose)
    - status: Filter by status (optional)
    """
    try:
        query = request.query_params.get("q", "").strip()

        if not query:
            return Response(
                {"error": "Search query 'q' is required"},
                status=400
            )

        entries = EntryLog.objects.filter(
            Q(name_snapshot__icontains=query) |
            Q(vehicle_no__icontains=query) |
            Q(purpose__icontains=query) |
            Q(visitor__name__icontains=query) |
            Q(labour__name__icontains=query) |
            Q(visitor__mobile__icontains=query) |
            Q(labour__mobile__icontains=query)
        )

        # Optional status filter
        status_filter = request.query_params.get("status")
        if status_filter:
            entries = entries.filter(status=status_filter.upper())

        entries = entries.order_by("-entry_time")[:50]  # Limit to 50 results

        serializer = EntryLogSerializer(entries, many=True)
        return Response({
            "query": query,
            "count": len(serializer.data),
            "results": serializer.data
        })
    except Exception as e:
        return Response({"error": str(e)}, status=400)


@api_view(["GET"])
@permission_classes([IsAuthenticated, HasCompanyContext, CanViewEntry])
def check_person_status(request):
    """
    Check if a visitor or labour is currently inside.

    Query Parameters:
    - visitor: Visitor ID
    - labour: Labour ID
    """
    try:
        visitor_id = request.query_params.get("visitor")
        labour_id = request.query_params.get("labour")

        if not visitor_id and not labour_id:
            return Response(
                {"error": "Either 'visitor' or 'labour' parameter is required"},
                status=400
            )

        if visitor_id:
            visitor = get_object_or_404(Visitor, pk=visitor_id)
            current_entry = EntryLog.objects.filter(
                visitor=visitor,
                status="IN"
            ).first()

            return Response({
                "person_type": "visitor",
                "person_id": visitor.id,
                "name": visitor.name,
                "is_inside": current_entry is not None,
                "current_entry": EntryLogSerializer(current_entry).data if current_entry else None,
                "blacklisted": visitor.blacklisted
            })

        if labour_id:
            labour = get_object_or_404(Labour, pk=labour_id)
            current_entry = EntryLog.objects.filter(
                labour=labour,
                status="IN"
            ).first()

            # Check permit validity
            permit_valid = True
            if labour.permit_valid_till:
                permit_valid = labour.permit_valid_till >= timezone.now().date()

            return Response({
                "person_type": "labour",
                "person_id": labour.id,
                "name": labour.name,
                "is_inside": current_entry is not None,
                "current_entry": EntryLogSerializer(current_entry).data if current_entry else None,
                "is_active": labour.is_active,
                "permit_valid": permit_valid,
                "permit_valid_till": labour.permit_valid_till
            })

    except Exception as e:
        return Response({"error": str(e)}, status=400)


# -------------------------
# Bulk Entry / Exit APIs
# -------------------------

@api_view(["POST"])
@permission_classes([IsAuthenticated, HasCompanyContext, CanCreateEntry])
def bulk_create_entry(request):
    """Create entry logs for multiple labours of a contractor at once."""
    serializer = BulkLabourEntryRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({"error": serializer.errors}, status=400)

    try:
        result = EntryService.bulk_create_entry(
            serializer.validated_data, request.user
        )
        return Response({
            "total_requested": result["total_requested"],
            "total_created": result["total_created"],
            "total_skipped": result["total_skipped"],
            "results": result["results"],
            "entries": EntryLogSerializer(result["entries"], many=True).data,
        })
    except Exception as e:
        return Response({"error": str(e)}, status=400)


@api_view(["POST"])
@permission_classes([IsAuthenticated, HasCompanyContext, CanExitEntry])
def bulk_exit_entry(request):
    """Mark exit for multiple labours of a contractor at once."""
    serializer = BulkLabourExitRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({"error": serializer.errors}, status=400)

    try:
        result = EntryService.bulk_exit_entry(serializer.validated_data)
        return Response({
            "total_requested": result["total_requested"],
            "total_exited": result["total_exited"],
            "total_skipped": result["total_skipped"],
            "results": result["results"],
        })
    except Exception as e:
        return Response({"error": str(e)}, status=400)


@api_view(["GET"])
@permission_classes([IsAuthenticated, HasCompanyContext, CanViewEntry])
def contractor_labours_for_entry(request, contractor_id):
    """Get all active labours for a contractor with their current entry status."""
    try:
        contractor = get_object_or_404(Contractor, pk=contractor_id, is_active=True)
        labours = Labour.objects.filter(
            contractor=contractor, is_active=True
        ).order_by("name")

        inside_labour_ids = set(
            EntryLog.objects.filter(
                labour__in=labours, status="IN"
            ).values_list("labour_id", flat=True)
        )

        results = []
        for labour in labours:
            results.append({
                "id": labour.id,
                "name": labour.name,
                "mobile": labour.mobile,
                "skill_type": labour.skill_type,
                "photo": labour.photo.url if labour.photo else None,
                "permit_valid_till": labour.permit_valid_till,
                "is_inside": labour.id in inside_labour_ids,
            })

        return Response({
            "contractor_id": contractor.id,
            "contractor_name": contractor.contractor_name,
            "total_active_labours": len(results),
            "total_currently_inside": len(inside_labour_ids),
            "labours": results,
        })
    except Exception as e:
        return Response({"error": str(e)}, status=400)
