from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .models.driver import Driver
from .serializers import DriverSerializer, DriverNameSerializer


class DriverListCreateAPI(APIView):
    """
    GET  -> List all drivers
    POST -> Create a new driver
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        drivers = Driver.objects.all().order_by("-created_at")
        serializer = DriverSerializer(drivers, many=True,context={'request': request})
        return Response(serializer.data)

    def post(self, request):
        serializer = DriverSerializer(data=request.data,context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save(created_by=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class DriverDetailAPI(APIView):
    """
    GET  -> Fetch driver by ID
    PUT  -> Update driver details
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        driver = get_object_or_404(Driver, id=id)
        serializer = DriverSerializer(driver, context={'request': request})
        return Response(serializer.data)

    def put(self, request, id):
        driver = get_object_or_404(Driver, id=id)
        serializer = DriverSerializer(
            driver,
            data=request.data,
            partial=True,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by=request.user)
        return Response(serializer.data)


class DriverNameListAPI(APIView):
    """
    GET -> List all drivers with id and name only
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        drivers = Driver.objects.all().order_by("name")
        serializer = DriverNameSerializer(drivers, many=True)
        return Response(serializer.data)