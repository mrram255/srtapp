from django.urls import path

from .accounting_views import (
    BudgetListView,
    ChartOfAccountListView,
    FeeReceiptView,
    JournalEntryListView,
    PayslipListView,
    PayrollRunListView,
    RazorpayCreateOrderView,
    RazorpayVerifyView,
    SalaryStructureListView,
    VendorListView,
)
from .views import (
    FeeDefaultersView,
    FeePaymentListView,
    FeeStructureListView,
    StudentFeeAccountListView,
)

urlpatterns = [
    path('structures/', FeeStructureListView.as_view(), name='fee_structure_list'),
    path('payments/', FeePaymentListView.as_view(), name='fee_payment_list'),
    path('payments/<uuid:pk>/receipt/', FeeReceiptView.as_view(), name='fee_receipt'),
    path('accounts/', StudentFeeAccountListView.as_view(), name='fee_account_list'),
    path('defaulters/', FeeDefaultersView.as_view(), name='fee_defaulters'),
    path('fees/', FeePaymentListView.as_view(), name='fee_list'),
    path('accounting/accounts/', ChartOfAccountListView.as_view(), name='chart_of_accounts'),
    path('accounting/journal/', JournalEntryListView.as_view(), name='journal_entries'),
    path('accounting/vendors/', VendorListView.as_view(), name='vendors'),
    path('accounting/budgets/', BudgetListView.as_view(), name='budgets'),
    path('payroll/structures/', SalaryStructureListView.as_view(), name='salary_structures'),
    path('payroll/runs/', PayrollRunListView.as_view(), name='payroll_runs'),
    path('payroll/payslips/', PayslipListView.as_view(), name='payslips'),
    path('razorpay/create-order/', RazorpayCreateOrderView.as_view(), name='razorpay_create_order'),
    path('razorpay/verify/', RazorpayVerifyView.as_view(), name='razorpay_verify'),
]
