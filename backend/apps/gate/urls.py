from django.urls import path

from .views import GateLogListView

urlpatterns = [
    path('', GateLogListView.as_view(), name='gate_log_list'),
]
