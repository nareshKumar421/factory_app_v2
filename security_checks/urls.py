from django.urls import path
from .views import (
    SecurityCheckCreateUpdateAPI,
    SecurityCheckDetailAPI,
    SubmitSecurityCheckAPI,
)

urlpatterns = [
    path(
        "gate-entries/<int:gate_entry_id>/security/",
        SecurityCheckCreateUpdateAPI.as_view()
    ),
    path(
        "gate-entries/<int:gate_entry_id>/security/view/",
        SecurityCheckDetailAPI.as_view()
    ),
    path(
        "security/<int:security_id>/submit/",
        SubmitSecurityCheckAPI.as_view()
    ),
]
