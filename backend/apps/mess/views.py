from apps.core.responses import APIResponse
from apps.core.views import BaseAPIView

from .models import MessFeedback, MessMenu
from .serializers import (
    MessFeedbackSerializer,
    MessFeedbackWriteSerializer,
    MessMenuSerializer,
    MessMenuWriteSerializer,
)


def _scope_college_models(queryset, user):
    if user.role == 'SUPER_ADMIN':
        return queryset
    if getattr(user, 'college_id', None):
        return queryset.filter(college_id=user.college_id)
    return queryset.none()


def _scope_mess_feedback(queryset, user):
    if user.role == 'SUPER_ADMIN':
        return queryset
    if user.role == 'ADMIN' and getattr(user, 'college_id', None):
        return queryset.filter(college_id=user.college_id)
    if user.role == 'STUDENT':
        return queryset.filter(student__user=user)
    return queryset.none()


class MessMenuListView(BaseAPIView):
    allowed_roles = ['SUPER_ADMIN', 'ADMIN', 'TEACHER', 'STUDENT']

    def get(self, request):
        queryset = MessMenu.objects.filter(is_deleted=False, is_active=True)
        queryset = _scope_college_models(queryset, request.user)

        day = request.query_params.get('day')
        meal_type = request.query_params.get('meal_type')

        if day:
            queryset = queryset.filter(day=day.upper())
        if meal_type:
            queryset = queryset.filter(meal_type=meal_type.upper())

        return APIResponse.paginated(queryset, MessMenuSerializer, request)

    def post(self, request):
        if request.user.role not in ('SUPER_ADMIN', 'ADMIN'):
            return APIResponse.error(message='Access denied.', status=403)

        college = request.user.college
        if request.user.role == 'SUPER_ADMIN':
            from apps.colleges.models import College

            cid = request.data.get('college')
            if not cid:
                return APIResponse.error(message='college is required.', status=400)
            college = College.objects.filter(pk=cid, is_deleted=False).first()
            if not college:
                return APIResponse.error(message='Invalid college.', status=400)

        if college is None:
            return APIResponse.error(message='College context required.', status=400)

        serializer = MessMenuWriteSerializer(data=request.data, context={'request': request, 'college': college})
        if not serializer.is_valid():
            return APIResponse.error(message='Invalid input.', errors=serializer.errors)

        menu = serializer.save()
        return APIResponse.success(data=MessMenuSerializer(menu).data, message='Menu updated.', status=201)


class MessFeedbackListView(BaseAPIView):
    allowed_roles = ['SUPER_ADMIN', 'ADMIN', 'STUDENT']

    def get(self, request):
        queryset = MessFeedback.objects.filter(is_deleted=False).select_related('student', 'menu')
        queryset = _scope_mess_feedback(queryset, request.user)
        return APIResponse.paginated(queryset, MessFeedbackSerializer, request)

    def post(self, request):
        if request.user.role != 'STUDENT':
            return APIResponse.error(message='Access denied.', status=403)

        payload = request.data.copy()
        try:
            payload['student'] = str(request.user.student_profile.pk)
        except Exception:
            return APIResponse.error(message='Student profile required.', status=400)

        serializer = MessFeedbackWriteSerializer(data=payload, context={'request': request})
        if not serializer.is_valid():
            return APIResponse.error(message='Invalid input.', errors=serializer.errors)

        feedback = serializer.save()
        return APIResponse.success(
            data=MessFeedbackSerializer(feedback).data,
            message='Feedback submitted.',
            status=201,
        )
