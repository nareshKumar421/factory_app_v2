from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register("person-types", PersonTypeViewSet)
router.register("gates", GateViewSet)
router.register("contractors", ContractorViewSet)
router.register("visitors", VisitorViewSet)
router.register("labours", LabourViewSet)

urlpatterns = [
    path("", include(router.urls)),

    # Entry CRUD
    path("entry/create/", create_entry),
    path("entry/<int:pk>/", entry_detail),

    path("entry/<int:pk>/exit/", exit_entry),
    path("entry/<int:pk>/cancel/", cancel_entry),
    path("entry/<int:pk>/update/", update_entry),

    # Entry Lists & Filters
    path("entry/inside/", inside_list),
    path("entries/", entries_by_date),
    path("entries/search/", search_entries),

    # History & Status
    path("visitor/<int:visitor_id>/history/", visitor_entry_history),
    path("labour/<int:labour_id>/history/", labour_entry_history),
    path("check-status/", check_person_status),

    # Dashboard
    path("dashboard/", dashboard_stats),
]
