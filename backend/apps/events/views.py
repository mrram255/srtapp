from django.db import IntegrityError

from apps.colleges.models import College

from apps.core.responses import APIResponse
from apps.core.views import BaseAPIView

from .models import Event, EventRegistration
from .serializers import (
    EventRegistrationSerializer,
    EventRegistrationWriteSerializer,
    EventSerializer,
    EventWriteSerializer,
)


def _scope_events(queryset, user):
    if user.role == 'SUPER_ADMIN':
        return queryset
    if not getattr(user, 'college_id', None):
        return queryset.none()
    qs = queryset.filter(college_id=user.college_id)
    if user.role not in ('SUPER_ADMIN', 'ADMIN', 'HOD'):
        qs = qs.filter(is_public=True)
    return qs


def _scope_event_registrations(queryset, user):
    if user.role == 'SUPER_ADMIN':
        return queryset
    if user.role in ('ADMIN', 'TEACHER') and getattr(user, 'college_id', None):
        return queryset.filter(college_id=user.college_id)
    if user.role == 'STUDENT':
        return queryset.filter(user=user)
    return queryset.none()


class EventListView(BaseAPIView):
    allowed_roles = ['SUPER_ADMIN', 'ADMIN', 'HOD', 'TEACHER', 'STUDENT', 'PARENT']

    def get(self, request):
        queryset = Event.objects.filter(is_deleted=False, is_active=True).select_related(
            'organizer',
            'department',
        )
        queryset = _scope_events(queryset, request.user)

        event_type = request.query_params.get('event_type')
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        is_public = request.query_params.get('is_public')

        if event_type:
            queryset = queryset.filter(event_type=event_type.upper())
        if date_from:
            queryset = queryset.filter(start_datetime__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(start_datetime__date__lte=date_to)
        if is_public is not None:
            queryset = queryset.filter(is_public=is_public.lower() == 'true')

        return APIResponse.paginated(queryset, EventSerializer, request)

    def post(self, request):
        if request.user.role not in ('SUPER_ADMIN', 'ADMIN', 'HOD'):
            return APIResponse.error(message='Access denied.', status=403)

        college = request.user.college
        if request.user.role == 'SUPER_ADMIN':
            cid = request.data.get('college')
            if not cid:
                return APIResponse.error(message='college is required.', status=400)
            college = College.objects.filter(pk=cid, is_deleted=False).first()
            if not college:
                return APIResponse.error(message='Invalid college.', status=400)

        if college is None:
            return APIResponse.error(message='College context required.', status=400)

        serializer = EventWriteSerializer(data=request.data, context={'request': request, 'college': college})
        if not serializer.is_valid():
            return APIResponse.error(message='Invalid input.', errors=serializer.errors)

        event = serializer.save()
        return APIResponse.success(data=EventSerializer(event).data, message='Event created.', status=201)


class EventRegistrationListView(BaseAPIView):
    allowed_roles = ['SUPER_ADMIN', 'ADMIN', 'TEACHER', 'STUDENT']

    def get(self, request):
        queryset = EventRegistration.objects.filter(is_deleted=False).select_related('event', 'user')
        queryset = _scope_event_registrations(queryset, request.user)

        event_id = request.query_params.get('event')
        user_id = request.query_params.get('user')
        status_param = request.query_params.get('status')

        if event_id:
            queryset = queryset.filter(event_id=event_id)
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        if status_param:
            queryset = queryset.filter(status=status_param.upper())

        return APIResponse.paginated(queryset, EventRegistrationSerializer, request)

    def post(self, request):
        serializer = EventRegistrationWriteSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return APIResponse.error(message='Invalid input.', errors=serializer.errors)

        event = serializer.validated_data['event']

        if event.max_participants is not None:
            current = EventRegistration.objects.filter(event=event, status='REGISTERED', is_deleted=False).count()
            if current >= event.max_participants:
                return APIResponse.error(message='Event is full.', status=400)

        try:
            registration = serializer.save()
        except IntegrityError:
            return APIResponse.error(message='Already registered for this event.', status=400)

        return APIResponse.success(
            data=EventRegistrationSerializer(registration).data,
            message='Registered for event.',
            status=201,
        )
