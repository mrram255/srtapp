from django.db.models import F

from apps.core.responses import APIResponse
from apps.core.views import BaseAPIView

from .models import Hostel, HostelAllocation, Room
from .serializers import HostelAllocationSerializer, HostelAllocationWriteSerializer, HostelSerializer, RoomSerializer


def _scope_college_models(queryset, user):
    if user.role == 'SUPER_ADMIN':
        return queryset
    if getattr(user, 'college_id', None):
        return queryset.filter(college_id=user.college_id)
    return queryset.none()


def _scope_allocations(queryset, user):
    if user.role == 'SUPER_ADMIN':
        return queryset
    if user.role == 'ADMIN' and getattr(user, 'college_id', None):
        return queryset.filter(college_id=user.college_id)
    if user.role == 'STUDENT':
        return queryset.filter(student__user=user)
    return queryset.none()


class HostelListView(BaseAPIView):
    allowed_roles = ['SUPER_ADMIN', 'ADMIN', 'STUDENT', 'PARENT']

    def get(self, request):
        queryset = Hostel.objects.filter(is_deleted=False, is_active=True)
        queryset = _scope_college_models(queryset, request.user)
        return APIResponse.paginated(queryset, HostelSerializer, request)


class RoomListView(BaseAPIView):
    allowed_roles = ['SUPER_ADMIN', 'ADMIN', 'STUDENT']

    def get(self, request):
        queryset = Room.objects.filter(is_deleted=False, is_active=True).select_related('hostel')
        queryset = _scope_college_models(queryset, request.user)

        hostel_id = request.query_params.get('hostel')
        available = request.query_params.get('available')

        if hostel_id:
            queryset = queryset.filter(hostel_id=hostel_id)
        if available and available.lower() in ('1', 'true', 'yes'):
            queryset = queryset.filter(occupied__lt=F('capacity'))

        return APIResponse.paginated(queryset, RoomSerializer, request)


class HostelAllocationListView(BaseAPIView):
    allowed_roles = ['SUPER_ADMIN', 'ADMIN', 'STUDENT']

    def get(self, request):
        queryset = HostelAllocation.objects.filter(is_deleted=False).select_related(
            'student',
            'room',
            'hostel',
        )
        queryset = _scope_allocations(queryset, request.user)

        student_id = request.query_params.get('student')
        status_param = request.query_params.get('status')

        if student_id:
            queryset = queryset.filter(student_id=student_id)
        if status_param:
            queryset = queryset.filter(status=status_param.upper())

        return APIResponse.paginated(queryset, HostelAllocationSerializer, request)

    def post(self, request):
        if request.user.role not in ('SUPER_ADMIN', 'ADMIN'):
            return APIResponse.error(message='Access denied.', status=403)

        serializer = HostelAllocationWriteSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return APIResponse.error(message='Invalid input.', errors=serializer.errors)

        allocation = serializer.save()
        return APIResponse.success(
            data=HostelAllocationSerializer(allocation).data,
            message='Hostel allocated.',
            status=201,
        )
