from apps.core.responses import APIResponse
from apps.core.views import BaseAPIView

from .models import BusRoute, BusStop, TransportAllocation
from .serializers import BusRouteSerializer, BusStopSerializer, TransportAllocationSerializer


def _scope_college_models(queryset, user):
    if user.role == 'SUPER_ADMIN':
        return queryset
    if getattr(user, 'college_id', None):
        return queryset.filter(college_id=user.college_id)
    return queryset.none()


def _scope_transport_allocations(queryset, user):
    if user.role == 'SUPER_ADMIN':
        return queryset
    if user.role == 'ADMIN' and getattr(user, 'college_id', None):
        return queryset.filter(college_id=user.college_id)
    if user.role == 'STUDENT':
        return queryset.filter(student__user=user)
    return queryset.none()


class BusRouteListView(BaseAPIView):
    allowed_roles = ['SUPER_ADMIN', 'ADMIN', 'STUDENT', 'PARENT']

    def get(self, request):
        queryset = BusRoute.objects.filter(is_deleted=False, is_active=True)
        queryset = _scope_college_models(queryset, request.user)
        return APIResponse.paginated(queryset, BusRouteSerializer, request)


class BusStopListView(BaseAPIView):
    allowed_roles = ['SUPER_ADMIN', 'ADMIN', 'STUDENT']

    def get(self, request):
        queryset = BusStop.objects.filter(is_deleted=False).select_related('route')
        queryset = _scope_college_models(queryset, request.user)

        route_id = request.query_params.get('route')
        if route_id:
            queryset = queryset.filter(route_id=route_id)

        return APIResponse.paginated(queryset, BusStopSerializer, request)


class TransportAllocationListView(BaseAPIView):
    allowed_roles = ['SUPER_ADMIN', 'ADMIN', 'STUDENT']

    def get(self, request):
        queryset = TransportAllocation.objects.filter(is_deleted=False).select_related(
            'student',
            'route',
            'pickup_stop',
            'drop_stop',
        )
        queryset = _scope_transport_allocations(queryset, request.user)

        student_id = request.query_params.get('student')
        route_id = request.query_params.get('route')

        if student_id:
            queryset = queryset.filter(student_id=student_id)
        if route_id:
            queryset = queryset.filter(route_id=route_id)

        return APIResponse.paginated(queryset, TransportAllocationSerializer, request)
