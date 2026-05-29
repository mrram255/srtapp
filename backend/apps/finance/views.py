from apps.core.responses import APIResponse
from apps.core.views import BaseAPIView

from .models import FeePayment, FeeStructure, StudentFeeAccount
from .serializers import (
    FeePaymentSerializer,
    FeePaymentWriteSerializer,
    FeeStructureSerializer,
    StudentFeeAccountSerializer,
)
from .services import FinanceService


def _scope_fee_structure(queryset, user):
    role = user.role
    if role == 'SUPER_ADMIN':
        return queryset
    if role not in ('ADMIN', 'ACCOUNTANT'):
        return queryset.none()
    if not getattr(user, 'college_id', None):
        return queryset.none()
    return queryset.filter(college=user.college)


def _scope_fee_account(queryset, user):
    role = user.role
    if role == 'SUPER_ADMIN':
        return queryset
    if role in ('ADMIN', 'ACCOUNTANT'):
        return queryset.filter(college=user.college)
    if role == 'STUDENT':
        return queryset.filter(student__user=user)
    if role == 'PARENT':
        try:
            wards = user.parent_profile.wards.values_list('pk', flat=True)
        except Exception:
            return queryset.none()
        return queryset.filter(student_id__in=wards)
    return queryset.none()


def _scope_fee_payment(queryset, user):
    role = user.role
    if role == 'SUPER_ADMIN':
        return queryset
    if role in ('ADMIN', 'ACCOUNTANT'):
        return queryset.filter(college=user.college)
    if role == 'STUDENT':
        return queryset.filter(student__user=user)
    if role == 'PARENT':
        try:
            wards = user.parent_profile.wards.values_list('pk', flat=True)
        except Exception:
            return queryset.none()
        return queryset.filter(student_id__in=wards)
    return queryset.none()


class FeeStructureListView(BaseAPIView):
    allowed_roles = ['SUPER_ADMIN', 'ADMIN', 'ACCOUNTANT']

    def get(self, request):
        queryset = FeeStructure.objects.filter(is_deleted=False, is_active=True).select_related(
            'department',
            'branch',
            'academic_year',
        )
        queryset = _scope_fee_structure(queryset, request.user)
        return APIResponse.paginated(queryset, FeeStructureSerializer, request)


class FeePaymentListView(BaseAPIView):
    allowed_roles = ['SUPER_ADMIN', 'ADMIN', 'ACCOUNTANT', 'STUDENT', 'PARENT']

    def get(self, request):
        queryset = FeePayment.objects.filter(is_deleted=False).select_related(
            'student',
            'fee_structure',
        )
        queryset = _scope_fee_payment(queryset, request.user)

        student_id = request.query_params.get('student')
        status = request.query_params.get('status')

        if student_id:
            queryset = queryset.filter(student_id=student_id)
        if status:
            queryset = queryset.filter(status=status.upper())

        return APIResponse.paginated(queryset, FeePaymentSerializer, request)

    def post(self, request):
        if request.user.role not in ('SUPER_ADMIN', 'ADMIN', 'ACCOUNTANT'):
            return APIResponse.error(message='Access denied.', status=403)

        serializer = FeePaymentWriteSerializer(data=request.data)
        if not serializer.is_valid():
            return APIResponse.error(message='Invalid input.', errors=serializer.errors)

        validated = serializer.validated_data
        if request.user.role != 'SUPER_ADMIN':
            if validated['student'].college_id != request.user.college_id:
                return APIResponse.error(message='Invalid student.', status=403)

        payment = serializer.save()
        return APIResponse.success(
            data=FeePaymentSerializer(payment).data,
            message='Payment recorded.',
            status=201,
        )


class FeeDefaultersView(BaseAPIView):
    allowed_roles = ['SUPER_ADMIN', 'ADMIN', 'ACCOUNTANT']

    def get(self, request):
        college = request.user.college
        if request.user.role == 'SUPER_ADMIN' and request.query_params.get('college'):
            from apps.colleges.models import College

            college = College.objects.filter(pk=request.query_params['college']).first()
        if college is None:
            return APIResponse.error(message='College context required.', status=400)
        accounts = _scope_fee_account(FinanceService.list_defaulters(college), request.user)
        return APIResponse.paginated(accounts, StudentFeeAccountSerializer, request)


class StudentFeeAccountListView(BaseAPIView):
    allowed_roles = ['SUPER_ADMIN', 'ADMIN', 'ACCOUNTANT', 'STUDENT', 'PARENT']

    def get(self, request):
        queryset = StudentFeeAccount.objects.filter(is_deleted=False).select_related(
            'student',
            'fee_structure',
        )
        queryset = _scope_fee_account(queryset, request.user)
        student_id = request.query_params.get('student')
        if student_id:
            queryset = queryset.filter(student_id=student_id)
        return APIResponse.paginated(queryset, StudentFeeAccountSerializer, request)
