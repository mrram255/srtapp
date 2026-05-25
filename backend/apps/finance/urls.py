from django.urls import path

from .views import FeePaymentListView, FeeStructureListView

urlpatterns = [
    path('structures/', FeeStructureListView.as_view(), name='fee_structure_list'),
    path('payments/', FeePaymentListView.as_view(), name='fee_payment_list'),
]
