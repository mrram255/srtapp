import uuid
from apps.core.responses import APIResponse
from apps.core.views import BaseAPIView
from apps.core.storage import MinIOStorage
from .models import StudyMaterial
from .serializers import StudyMaterialSerializer, StudyMaterialWriteSerializer


def _scope_materials(queryset, user):
    role = user.role
    if role == 'SUPER_ADMIN':
        return queryset
    if role == 'TEACHER':
        return queryset.filter(college=user.college, teacher__user=user)
    if role == 'STUDENT':
        from apps.students.models import Student
        try:
            sp = Student.objects.get(user=user)
        except Student.DoesNotExist:
            return queryset.none()
        return queryset.filter(
            college=user.college,
            is_published=True,
            semester=sp.semester,
        ).exclude(access_level='BATCH', section__isnull=False).union(
            queryset.filter(
                college=user.college, is_published=True,
                semester=sp.semester, section__iexact=sp.section,
            )
        )
    if role in ('ADMIN', 'HOD', 'LIBRARIAN'):
        return queryset.filter(college=user.college)
    return queryset.none()


class StudyMaterialListView(BaseAPIView):
    allowed_roles = ['SUPER_ADMIN', 'ADMIN', 'HOD', 'TEACHER', 'STUDENT']

    def get(self, request):
        queryset = StudyMaterial.objects.filter(is_deleted=False).select_related(
            'subject', 'teacher', 'teacher__user', 'department'
        )
        queryset = _scope_materials(queryset, request.user)

        subject_id = request.query_params.get('subject')
        material_type = request.query_params.get('type')
        semester = request.query_params.get('semester')
        search = request.query_params.get('search')
        tag = request.query_params.get('tag')

        if subject_id:
            queryset = queryset.filter(subject_id=subject_id)
        if material_type:
            queryset = queryset.filter(material_type=material_type.upper())
        if semester:
            queryset = queryset.filter(semester=semester)
        if search:
            queryset = queryset.filter(title__icontains=search)
        if tag:
            queryset = queryset.filter(tags__icontains=tag)

        return APIResponse.paginated(queryset, StudyMaterialSerializer, request)

    def post(self, request):
        if request.user.role not in ('SUPER_ADMIN', 'ADMIN', 'HOD', 'TEACHER'):
            return APIResponse.error(message='Access denied.', status=403)

        serializer = StudyMaterialWriteSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return APIResponse.error(message='Invalid input.', errors=serializer.errors)

        material = serializer.save()
        return APIResponse.success(
            data=StudyMaterialSerializer(material).data,
            message='Study material created.',
            status=201,
        )


class StudyMaterialDetailView(BaseAPIView):
    allowed_roles = ['SUPER_ADMIN', 'ADMIN', 'HOD', 'TEACHER', 'STUDENT']

    def get(self, request, pk):
        try:
            material = StudyMaterial.objects.select_related(
                'subject', 'teacher', 'teacher__user', 'department'
            ).get(pk=pk, is_deleted=False)
        except StudyMaterial.DoesNotExist:
            return APIResponse.error(message='Material not found.', status=404)

        # Track download count
        material.download_count += 1
        material.save(update_fields=['download_count'])

        return APIResponse.success(data=StudyMaterialSerializer(material).data)

    def patch(self, request, pk):
        if request.user.role not in ('SUPER_ADMIN', 'ADMIN', 'HOD', 'TEACHER'):
            return APIResponse.error(message='Access denied.', status=403)
        try:
            material = StudyMaterial.objects.get(pk=pk, is_deleted=False)
        except StudyMaterial.DoesNotExist:
            return APIResponse.error(message='Material not found.', status=404)

        if request.user.role == 'TEACHER' and material.teacher.user_id != request.user.id:
            return APIResponse.error(message='You can only edit your own materials.', status=403)

        # New upload = new version
        if 'file_url' in request.data and request.data['file_url'] != material.file_url:
            material.version += 1
            material.save(update_fields=['version'])

        serializer = StudyMaterialWriteSerializer(
            material, data=request.data, partial=True, context={'request': request}
        )
        if not serializer.is_valid():
            return APIResponse.error(message='Invalid input.', errors=serializer.errors)
        serializer.save()
        return APIResponse.success(data=StudyMaterialSerializer(material).data, message='Updated.')

    def delete(self, request, pk):
        if request.user.role not in ('SUPER_ADMIN', 'ADMIN', 'HOD', 'TEACHER'):
            return APIResponse.error(message='Access denied.', status=403)
        try:
            material = StudyMaterial.objects.get(pk=pk, is_deleted=False)
        except StudyMaterial.DoesNotExist:
            return APIResponse.error(message='Material not found.', status=404)

        if request.user.role == 'TEACHER' and material.teacher.user_id != request.user.id:
            return APIResponse.error(message='You can only delete your own materials.', status=403)

        material.is_deleted = True
        material.save(update_fields=['is_deleted'])
        return APIResponse.success(message='Deleted.')


class StudyMaterialUploadView(BaseAPIView):
    """Upload PDF/video to MinIO, return URL."""
    allowed_roles = ['SUPER_ADMIN', 'ADMIN', 'HOD', 'TEACHER']

    def post(self, request):
        file = request.FILES.get('file')
        if not file:
            return APIResponse.error(message='file is required.')

        allowed = [
            'application/pdf',
            'video/mp4', 'video/mpeg', 'video/webm',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.ms-powerpoint',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            'image/jpeg', 'image/png',
        ]
        if file.content_type not in allowed:
            return APIResponse.error(message='File type not allowed.')

        max_size = 200 * 1024 * 1024  # 200MB
        if file.size > max_size:
            return APIResponse.error(message='File must be under 200MB.')

        storage = MinIOStorage()
        ext = file.name.rsplit('.', 1)[-1] if '.' in file.name else 'bin'
        filename = f"study-materials/{request.user.college_id}/{uuid.uuid4().hex}.{ext}"
        saved = storage.save(filename, file)
        url = storage.url(saved)

        return APIResponse.success(
            data={'url': url, 'filename': saved, 'size': file.size, 'type': file.content_type},
            message='File uploaded.',
            status=201,
        )
