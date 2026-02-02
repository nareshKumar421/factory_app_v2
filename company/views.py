from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated,DjangoModelPermissionsOrAnonReadOnly
from .models import Company
from .serializers import CompanySerializer
from .permissions import HasCompanyContext

class CompanyViewSet(ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissionsOrAnonReadOnly, HasCompanyContext]




