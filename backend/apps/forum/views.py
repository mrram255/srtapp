from django.db.models import Q
from apps.core.responses import APIResponse
from apps.core.views import BaseAPIView
from .models import ForumThread, ForumReply, ForumLike
from .serializers import ForumThreadSerializer, ForumReplySerializer


def _scope_threads(queryset, user):
    role = user.role
    if role == 'SUPER_ADMIN':
        return queryset
    return queryset.filter(college=user.college)


class ForumThreadListView(BaseAPIView):
    allowed_roles = ['SUPER_ADMIN', 'ADMIN', 'HOD', 'TEACHER', 'STUDENT']

    def get(self, request):
        queryset = ForumThread.objects.filter(is_deleted=False).select_related('author', 'subject', 'department')
        queryset = _scope_threads(queryset, request.user)

        subject_id = request.query_params.get('subject')
        dept_id = request.query_params.get('department')
        semester = request.query_params.get('semester')
        search = request.query_params.get('search')
        tag = request.query_params.get('tag')
        pinned = request.query_params.get('pinned')

        if subject_id:
            queryset = queryset.filter(subject_id=subject_id)
        if dept_id:
            queryset = queryset.filter(department_id=dept_id)
        if semester:
            queryset = queryset.filter(semester=semester)
        if search:
            queryset = queryset.filter(Q(title__icontains=search) | Q(body__icontains=search))
        if tag:
            queryset = queryset.filter(tags__icontains=tag)
        if pinned == 'true':
            queryset = queryset.filter(is_pinned=True)

        return APIResponse.paginated(queryset, ForumThreadSerializer, request)

    def post(self, request):
        data = request.data.copy()
        serializer = ForumThreadSerializer(data=data)
        if not serializer.is_valid():
            return APIResponse.error(message='Invalid input.', errors=serializer.errors)

        thread = serializer.save(
            author=request.user,
            college=request.user.college,
        )
        return APIResponse.success(data=ForumThreadSerializer(thread).data, message='Thread created.', status=201)


class ForumThreadDetailView(BaseAPIView):
    allowed_roles = ['SUPER_ADMIN', 'ADMIN', 'HOD', 'TEACHER', 'STUDENT']

    def get(self, request, pk):
        try:
            thread = ForumThread.objects.select_related('author', 'subject').get(pk=pk, is_deleted=False)
        except ForumThread.DoesNotExist:
            return APIResponse.error(message='Thread not found.', status=404)

        thread.view_count += 1
        thread.save(update_fields=['view_count'])

        replies = ForumReply.objects.filter(thread=thread, is_deleted=False, parent_reply=None).select_related('author')
        return APIResponse.success(data={
            'thread': ForumThreadSerializer(thread).data,
            'replies': ForumReplySerializer(replies, many=True).data,
        })

    def patch(self, request, pk):
        try:
            thread = ForumThread.objects.get(pk=pk, is_deleted=False)
        except ForumThread.DoesNotExist:
            return APIResponse.error(message='Thread not found.', status=404)

        if thread.author_id != request.user.id and request.user.role not in ('SUPER_ADMIN', 'ADMIN', 'HOD'):
            return APIResponse.error(message='Access denied.', status=403)

        # Admin can pin/close/flag
        allowed_fields = ['title', 'body', 'tags']
        if request.user.role in ('SUPER_ADMIN', 'ADMIN', 'HOD'):
            allowed_fields += ['is_pinned', 'is_closed', 'is_flagged']

        for field in allowed_fields:
            if field in request.data:
                setattr(thread, field, request.data[field])
        thread.save()
        return APIResponse.success(data=ForumThreadSerializer(thread).data, message='Updated.')

    def delete(self, request, pk):
        try:
            thread = ForumThread.objects.get(pk=pk, is_deleted=False)
        except ForumThread.DoesNotExist:
            return APIResponse.error(message='Thread not found.', status=404)

        if thread.author_id != request.user.id and request.user.role not in ('SUPER_ADMIN', 'ADMIN'):
            return APIResponse.error(message='Access denied.', status=403)

        thread.is_deleted = True
        thread.save(update_fields=['is_deleted'])
        return APIResponse.success(message='Thread deleted.')


class ForumReplyListView(BaseAPIView):
    allowed_roles = ['SUPER_ADMIN', 'ADMIN', 'HOD', 'TEACHER', 'STUDENT']

    def post(self, request, thread_pk):
        try:
            thread = ForumThread.objects.get(pk=thread_pk, is_deleted=False, college=request.user.college)
        except ForumThread.DoesNotExist:
            return APIResponse.error(message='Thread not found.', status=404)

        if thread.is_closed:
            return APIResponse.error(message='Thread is closed.', status=400)

        data = request.data.copy()
        data['thread'] = str(thread_pk)
        serializer = ForumReplySerializer(data=data)
        if not serializer.is_valid():
            return APIResponse.error(message='Invalid input.', errors=serializer.errors)

        reply = serializer.save(author=request.user, college=request.user.college)
        thread.reply_count = ForumReply.objects.filter(thread=thread, is_deleted=False).count()
        thread.save(update_fields=['reply_count'])

        return APIResponse.success(data=ForumReplySerializer(reply).data, message='Reply posted.', status=201)


class ForumReplyLikeView(BaseAPIView):
    """Like/unlike a reply."""
    allowed_roles = ['SUPER_ADMIN', 'ADMIN', 'HOD', 'TEACHER', 'STUDENT']

    def post(self, request, reply_pk):
        try:
            reply = ForumReply.objects.get(pk=reply_pk, is_deleted=False)
        except ForumReply.DoesNotExist:
            return APIResponse.error(message='Reply not found.', status=404)

        like, created = ForumLike.objects.get_or_create(user=request.user, reply=reply)
        if not created:
            like.delete()
            reply.like_count = max(0, reply.like_count - 1)
            msg = 'Like removed.'
        else:
            reply.like_count += 1
            msg = 'Liked.'
        reply.save(update_fields=['like_count'])
        return APIResponse.success(data={'like_count': reply.like_count, 'liked': created}, message=msg)
