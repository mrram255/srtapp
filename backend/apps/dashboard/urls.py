from django.urls import path

from .views import PrincipalDashboardView, SuperAdminDashboardView

urlpatterns = [
    path('super-admin/', SuperAdminDashboardView.as_view(), name='dashboard_super_admin'),
    path('principal/', PrincipalDashboardView.as_view(), name='dashboard_principal'),
]
