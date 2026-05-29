from django.utils import timezone

from apps.core.responses import APIResponse
from apps.core.views import BaseAPIView

from .models import ApprovalRequest, Meeting, StrategicPlanItem
from .serializers import (
    ApprovalRequestSerializer,
    ApprovalRequestWriteSerializer,
    MeetingSerializer,
    MeetingWriteSerializer,
    StrategicPlanItemSerializer,
)


def _scope_college(queryset, user):
    if user.role == 'SUPER_ADMIN':
        return queryset
    if getattr(user, 'college_id', None):
        return queryset.filter(college_id=user.college_id)
    return queryset.none()


class ApprovalListView(BaseAPIView):
    allowed_roles = ['SUPER_ADMIN', 'ADMIN', 'PRINCIPAL', 'VICE_PRINCIPAL', 'DEAN', 'HOD', 'REGISTRAR']

    def get(self, request):
        queryset = ApprovalRequest.objects.filter(is_deleted=False).select_related('requested_by')
        queryset = _scope_college(queryset, request.user)
        status_param = request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param.lower())
        return APIResponse.paginated(queryset, ApprovalRequestSerializer, request)

    def post(self, request):
        college = request.user.college
        if college is None and request.user.role != 'SUPER_ADMIN':
            return APIResponse.error(message='College context required.', status=400)
        serializer = ApprovalRequestWriteSerializer(data=request.data)
        if not serializer.is_valid():
            return APIResponse.error(message='Invalid input.', errors=serializer.errors)
        obj = serializer.save(college=college, requested_by=request.user)
        return APIResponse.success(
            data=ApprovalRequestSerializer(obj).data,
            message='Approval request created.',
            status=201,
        )


class ApprovalDetailView(BaseAPIView):
    allowed_roles = ['SUPER_ADMIN', 'ADMIN', 'PRINCIPAL', 'VICE_PRINCIPAL', 'DEAN']

    def post(self, request, pk, action):
        queryset = ApprovalRequest.objects.filter(pk=pk, is_deleted=False)
        queryset = _scope_college(queryset, request.user)
        obj = queryset.first()
        if not obj:
            return APIResponse.error(message='Not found.', status=404)
        if obj.status != 'pending':
            return APIResponse.error(message='Request already processed.', status=400)

        if action == 'approve':
            obj.status = 'approved'
        elif action == 'reject':
            obj.status = 'rejected'
        else:
            return APIResponse.error(message='Invalid action.', status=400)

        obj.reviewed_by = request.user
        obj.reviewed_at = timezone.now()
        obj.remarks = request.data.get('remarks', '')
        obj.save(update_fields=['status', 'reviewed_by', 'reviewed_at', 'remarks'])
        return APIResponse.success(data=ApprovalRequestSerializer(obj).data)


class MeetingListView(BaseAPIView):
    allowed_roles = ['SUPER_ADMIN', 'ADMIN', 'PRINCIPAL', 'VICE_PRINCIPAL', 'DEAN', 'HOD']

    def get(self, request):
        queryset = Meeting.objects.filter(is_deleted=False).select_related('organizer')
        queryset = _scope_college(queryset, request.user)
        return APIResponse.paginated(queryset, MeetingSerializer, request)

    def post(self, request):
        college = request.user.college
        if college is None:
            return APIResponse.error(message='College context required.', status=400)
        serializer = MeetingWriteSerializer(data=request.data)
        if not serializer.is_valid():
            return APIResponse.error(message='Invalid input.', errors=serializer.errors)
        obj = serializer.save(college=college, organizer=request.user)
        return APIResponse.success(data=MeetingSerializer(obj).data, status=201)


class MeetingDetailView(BaseAPIView):
    allowed_roles = ['SUPER_ADMIN', 'ADMIN', 'PRINCIPAL', 'VICE_PRINCIPAL', 'DEAN', 'HOD']

    def patch(self, request, pk):
        queryset = Meeting.objects.filter(pk=pk, is_deleted=False)
        queryset = _scope_college(queryset, request.user)
        obj = queryset.first()
        if not obj:
            return APIResponse.error(message='Not found.', status=404)
        serializer = MeetingWriteSerializer(obj, data=request.data, partial=True)
        if not serializer.is_valid():
            return APIResponse.error(message='Invalid input.', errors=serializer.errors)
        serializer.save()
        if 'minutes' in request.data:
            obj.minutes = request.data['minutes']
            obj.status = request.data.get('status', 'completed')
            obj.save(update_fields=['minutes', 'status'])
        return APIResponse.success(data=MeetingSerializer(obj).data)


class StrategicPlanListView(BaseAPIView):
    allowed_roles = ['SUPER_ADMIN', 'ADMIN', 'PRINCIPAL', 'VICE_PRINCIPAL', 'DEAN']

    def get(self, request):
        queryset = StrategicPlanItem.objects.filter(is_deleted=False)
        queryset = _scope_college(queryset, request.user)
        return APIResponse.paginated(queryset, StrategicPlanItemSerializer, request)

    def post(self, request):
        college = request.user.college
        if college is None:
            return APIResponse.error(message='College context required.', status=400)
        serializer = StrategicPlanItemSerializer(data=request.data)
        if not serializer.is_valid():
            return APIResponse.error(message='Invalid input.', errors=serializer.errors)
        obj = serializer.save(college=college, owner=request.user)
        return APIResponse.success(data=StrategicPlanItemSerializer(obj).data, status=201)
