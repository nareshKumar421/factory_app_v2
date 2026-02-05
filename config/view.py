from rest_framework.views import APIView
from rest_framework.response import Response        


class RootApiView(APIView):
    def get(self, request):
        return Response({
            "message": "Welcome to the Accounts API",
            "endpoints": {
                "login": "/login/",
                "change_password": "/change-password/",
                "token_refresh": "/token/refresh/",
                "me": "/me/",
                "departments": "/departments/",
            }
        })