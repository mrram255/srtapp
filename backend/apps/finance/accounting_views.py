from django.utils import timezone

from apps.core.responses import APIResponse
from apps.core.views import BaseAPIView

from .accounting_serializers import (
    BudgetSerializer,
    ChartOfAccountSerializer,
    JournalEntrySerializer,
    JournalEntryWriteSerializer,
    PaymentOrderSerializer,
    PayrollRunSerializer,
    PayslipSerializer,
    SalaryStructureSerializer,
    VendorSerializer,
)
from .accounting_service import AccountingService
from .models import Budget, ChartOfAccount, JournalEntry, PaymentOrder, PayrollRun, Payslip, SalaryStructure, Vendor
from .razorpay_service import RazorpayService
from .receipts import generate_fee_receipt_pdf


def _college_scope(queryset, user):
    if user.role == 'SUPER_ADMIN':
        return queryset
    if getattr(user, 'college_id', None):
        return queryset.filter(college_id=user.college_id)
    return queryset.none()


class ChartOfAccountListView(BaseAPIView):
    allowed_roles = ['SUPER_ADMIN', 'ADMIN', 'ACCOUNTANT']

    def get(self, request):
        qs = _college_scope(ChartOfAccount.objects.filter(is_deleted=False), request.user)
        return APIResponse.paginated(qs, ChartOfAccountSerializer, request)

    def post(self, request):
        college = request.user.college
        if not college:
            return APIResponse.error(message='College required.', status=400)
        ser = ChartOfAccountSerializer(data=request.data)
        if not ser.is_valid():
            return APIResponse.error(message='Invalid input.', errors=ser.errors)
        obj = ser.save(college=college)
        return APIResponse.success(data=ChartOfAccountSerializer(obj).data, status=201)


class JournalEntryListView(BaseAPIView):
    allowed_roles = ['SUPER_ADMIN', 'ADMIN', 'ACCOUNTANT']

    def get(self, request):
        qs = _college_scope(
            JournalEntry.objects.filter(is_deleted=False).prefetch_related('lines'),
            request.user,
        )
        return APIResponse.paginated(qs, JournalEntrySerializer, request)

    def post(self, request):
        college = request.user.college
        if not college:
            return APIResponse.error(message='College required.', status=400)
        ser = JournalEntryWriteSerializer(data=request.data)
        if not ser.is_valid():
            return APIResponse.error(message='Invalid input.', errors=ser.errors)
        try:
            entry = AccountingService.create_journal_entry(
                college=college,
                entry_date=ser.validated_data['entry_date'],
                description=ser.validated_data['description'],
                lines=ser.validated_data['lines'],
                posted_by=request.user,
            )
        except ValueError as exc:
            return APIResponse.error(message=str(exc), status=400)
        return APIResponse.success(
            data=JournalEntrySerializer(entry).data,
            message='Journal entry posted.',
            status=201,
        )


class VendorListView(BaseAPIView):
    allowed_roles = ['SUPER_ADMIN', 'ADMIN', 'ACCOUNTANT']

    def get(self, request):
        qs = _college_scope(Vendor.objects.filter(is_deleted=False), request.user)
        return APIResponse.paginated(qs, VendorSerializer, request)

    def post(self, request):
        college = request.user.college
        if not college:
            return APIResponse.error(message='College required.', status=400)
        ser = VendorSerializer(data=request.data)
        if not ser.is_valid():
            return APIResponse.error(message='Invalid input.', errors=ser.errors)
        obj = ser.save(college=college)
        return APIResponse.success(data=VendorSerializer(obj).data, status=201)


class BudgetListView(BaseAPIView):
    allowed_roles = ['SUPER_ADMIN', 'ADMIN', 'ACCOUNTANT']

    def get(self, request):
        qs = _college_scope(Budget.objects.filter(is_deleted=False).select_related('account'), request.user)
        return APIResponse.paginated(qs, BudgetSerializer, request)


class SalaryStructureListView(BaseAPIView):
    allowed_roles = ['SUPER_ADMIN', 'ADMIN', 'ACCOUNTANT']

    def get(self, request):
        qs = _college_scope(SalaryStructure.objects.filter(is_deleted=False), request.user)
        return APIResponse.paginated(qs, SalaryStructureSerializer, request)

    def post(self, request):
        college = request.user.college
        if not college:
            return APIResponse.error(message='College required.', status=400)
        ser = SalaryStructureSerializer(data=request.data)
        if not ser.is_valid():
            return APIResponse.error(message='Invalid input.', errors=ser.errors)
        obj = ser.save(college=college)
        return APIResponse.success(data=SalaryStructureSerializer(obj).data, status=201)


class PayrollRunListView(BaseAPIView):
    allowed_roles = ['SUPER_ADMIN', 'ADMIN', 'ACCOUNTANT']

    def get(self, request):
        qs = _college_scope(PayrollRun.objects.filter(is_deleted=False), request.user)
        return APIResponse.paginated(qs, PayrollRunSerializer, request)

    def post(self, request):
        college = request.user.college
        if not college:
            return APIResponse.error(message='College required.', status=400)
        month = int(request.data.get('month', timezone.localdate().month))
        year = int(request.data.get('year', timezone.localdate().year))
        run = AccountingService.process_payroll(
            college=college,
            month=month,
            year=year,
            processed_by=request.user,
        )
        return APIResponse.success(data=PayrollRunSerializer(run).data, status=201)


class PayslipListView(BaseAPIView):
    allowed_roles = ['SUPER_ADMIN', 'ADMIN', 'ACCOUNTANT']

    def get(self, request):
        qs = _college_scope(Payslip.objects.filter(is_deleted=False).select_related('staff'), request.user)
        run_id = request.query_params.get('payroll_run')
        if run_id:
            qs = qs.filter(payroll_run_id=run_id)
        return APIResponse.paginated(qs, PayslipSerializer, request)


class RazorpayCreateOrderView(BaseAPIView):
    allowed_roles = ['SUPER_ADMIN', 'ADMIN', 'ACCOUNTANT', 'STUDENT', 'PARENT']

    def post(self, request):
        from decimal import Decimal

        from apps.students.models import Student

        student_id = request.data.get('student')
        amount = Decimal(str(request.data.get('amount', 0)))
        if not student_id or amount <= 0:
            return APIResponse.error(message='student and amount required.', status=400)

        student = Student.objects.filter(pk=student_id, is_deleted=False).first()
        if not student:
            return APIResponse.error(message='Student not found.', status=404)

        order = RazorpayService.create_order(
            student=student,
            amount=amount,
            college=student.college,
        )
        from django.conf import settings as dj_settings

        data = PaymentOrderSerializer(order).data
        data['razorpay_key_id'] = getattr(dj_settings, 'RAZORPAY_KEY_ID', '')
        data['mock_mode'] = not RazorpayService.is_configured()
        return APIResponse.success(data=data, status=201)


class RazorpayVerifyView(BaseAPIView):
    allowed_roles = ['SUPER_ADMIN', 'ADMIN', 'ACCOUNTANT', 'STUDENT', 'PARENT']

    def post(self, request):
        order_id = request.data.get('razorpay_order_id')
        payment_id = request.data.get('razorpay_payment_id')
        signature = request.data.get('razorpay_signature', '')
        order = PaymentOrder.objects.filter(razorpay_order_id=order_id).first()
        if not order:
            return APIResponse.error(message='Order not found.', status=404)
        order = RazorpayService.mark_paid(order, payment_id, signature)
        if order.status == 'failed':
            return APIResponse.error(message='Payment verification failed.', status=400)
        return APIResponse.success(data=PaymentOrderSerializer(order).data, message='Payment verified.')


class FeeReceiptView(BaseAPIView):
    allowed_roles = ['SUPER_ADMIN', 'ADMIN', 'ACCOUNTANT', 'STUDENT', 'PARENT']

    def get(self, request, pk):
        from .models import FeePayment

        payment = FeePayment.objects.filter(pk=pk, is_deleted=False).select_related('student', 'college').first()
        if not payment:
            return APIResponse.error(message='Payment not found.', status=404)
        url = generate_fee_receipt_pdf(payment)
        return APIResponse.success(data={'receipt_url': url, 'receipt_number': payment.receipt_number})
