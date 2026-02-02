## Not Final working on this copy

from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied
from .models import UserCompany


class HasCompanyContext(BasePermission):

    def has_permission(self, request, view):
       
        # Extract company code from headers
        company_code = request.headers.get("Company-Code")

        # Validate presence and access
        if not company_code:
            raise PermissionDenied("Company-Code header is missing.")

        # 
        try:
            user_company = UserCompany.objects.get(
                user=request.user,
                is_active=True,
                company__code=company_code
            )
        except UserCompany.DoesNotExist:
            raise PermissionDenied("You do not have access to any companies.")

        # Attach for later use
        request.company = user_company

        return True
    

## Test This is the end of the code