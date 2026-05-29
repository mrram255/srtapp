from apps.core.responses import APIResponse
from apps.core.views import BaseAPIView

from .models import Message, MessageThread
from .serializers import (
    MessageSerializer,
    MessageThreadSerializer,
    MessageThreadWriteSerializer,
    MessageWriteSerializer,
)


def _thread_queryset_for_user(user):
    qs = MessageThread.objects.filter(is_deleted=False, is_active=True, participants=user)
    if user.role != 'SUPER_ADMIN' and getattr(user, 'college_id', None):
        qs = qs.filter(college_id=user.college_id)
    return qs.distinct()


class MessageThreadListView(BaseAPIView):
    allowed_roles = ['SUPER_ADMIN', 'ADMIN', 'HOD', 'TEACHER', 'STUDENT', 'PARENT']

    def get(self, request):
        queryset = (
            _thread_queryset_for_user(request.user)
            .select_related('created_by')
            .prefetch_related('participants')
        )
        return APIResponse.paginated(queryset, MessageThreadSerializer, request)

    def post(self, request):
        college = request.user.college
        if request.user.role == 'SUPER_ADMIN':
            college_id = request.data.get('college')
            if not college_id:
                return APIResponse.error(message='college is required.', status=400)
            from apps.colleges.models import College

            college = College.objects.filter(pk=college_id, is_deleted=False).first()
            if not college:
                return APIResponse.error(message='Invalid college.', status=400)

        if college is None:
            return APIResponse.error(message='College context required.', status=400)

        serializer = MessageThreadWriteSerializer(
            data=request.data,
            context={'request': request, 'college': college},
        )
        if not serializer.is_valid():
            return APIResponse.error(message='Invalid input.', errors=serializer.errors)

        thread = serializer.save()
        return APIResponse.success(
            data=MessageThreadSerializer(thread).data,
            message='Thread created.',
            status=201,
        )


class MessageListView(BaseAPIView):
    allowed_roles = ['SUPER_ADMIN', 'ADMIN', 'HOD', 'TEACHER', 'STUDENT', 'PARENT']

    def get(self, request):
        thread_id = request.query_params.get('thread')
        if not thread_id:
            queryset = _thread_queryset_for_user(request.user).select_related('created_by').prefetch_related('participants')
            return APIResponse.paginated(queryset, MessageThreadSerializer, request)

        thread = MessageThread.objects.filter(pk=thread_id, is_deleted=False).first()
        if not thread:
            return APIResponse.error(message='Thread not found.', status=404)

        if not thread.participants.filter(pk=request.user.pk).exists():
            return APIResponse.error(message='Access denied.', status=403)

        if request.user.role != 'SUPER_ADMIN' and getattr(request.user, 'college_id', None):
            if thread.college_id != request.user.college_id:
                return APIResponse.error(message='Access denied.', status=403)

        messages = Message.objects.filter(thread_id=thread_id, is_deleted=False).select_related('sender')
        return APIResponse.paginated(messages, MessageSerializer, request)

    def post(self, request):
        serializer = MessageWriteSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return APIResponse.error(message='Invalid input.', errors=serializer.errors)

        thread = serializer.validated_data['thread']
        if request.user.role != 'SUPER_ADMIN' and getattr(request.user, 'college_id', None):
            if thread.college_id != request.user.college_id:
                return APIResponse.error(message='Access denied.', status=403)

        message = serializer.save()
        return APIResponse.success(
            data=MessageSerializer(message).data,
            message='Message sent.',
            status=201,
        )
