from django.urls import path
from .views import DepartmentListView, LoginView
from .views import ChangePasswordView, MeView, CustomTokenRefreshView,UserListView

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("change-password/", ChangePasswordView.as_view()),
    path("token/refresh/", CustomTokenRefreshView.as_view(), name="token_refresh"),
    path("me/", MeView.as_view(), name="me"),
    path('users/', UserListView.as_view(), name='user-list'),

    path("departments/", DepartmentListView.as_view(), name="department-list"),
]
