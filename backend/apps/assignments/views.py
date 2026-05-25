import uuid
from django.utils import timezone
from apps.core.responses import APIResponse
from apps.core.views import BaseAPIView
from apps.core.storage import MinIOStorage
from apps.students.models import Student
from .models import Assignment, AssignmentSubmission
from .serializers import (
    AssignmentSerializer,
    AssignmentSubmissionSerializer,
    AssignmentWriteSerializer,
)


def _scope_assignments(queryset, user):
    role = user.role
    if role == 'SUPER_ADMIN':
        return queryset
    if role == 'TEACHER':
        return queryset.filter(teacher__user=user)
    if role == 'STUDENT':
        try:
            sp = user.student_profile
        except Student.DoesNotExist:
            return queryset.none()
        return queryset.filter(
            college_id=user.college_id,
            semester=sp.semester,
            section__iexact=sp.section,
            status='PUBLISHED',
            is_active=True,
        )
    if role in ('ADMIN', 'ACCOUNTANT', 'LIBRARIAN', 'SECURITY'):
        return queryset.filter(college=user.college)
    if role == 'HOD':
        return queryset.filter(college=user.college, department=user.department)
    return queryset.none()


def _scope_submissions(queryset, user):
    role = user.role
    if role == 'SUPER_ADMIN':
        return queryset
    if role == 'STUDENT':
        return queryset.filter(student__user=user)
    if role == 'TEACHER':
        return queryset.filter(assignment__teacher__user=user)
    if role == 'PARENT':
        try:
            wards = user.parent_profile.wards.values_list('pk', flat=True)
        except Exception:
            return queryset.none()
        return queryset.filter(student_id__in=wards)
    if role in ('ADMIN', 'ACCOUNTANT', 'LIBRARIAN', 'SECURITY'):
        return queryset.filter(college=user.college)
    if role == 'HOD':
        return queryset.filter(college=user.college, assignment__department=user.department)
    return queryset.none()


class AssignmentListView(BaseAPIView):
    allowed_roles = ['SUPER_ADMIN', 'ADMIN', 'HOD', 'TEACHER', 'STUDENT']

    def get(self, request):
        queryset = Assignment.objects.filter(is_deleted=False).select_related(
            'subject', 'teacher', 'teacher__user', 'department'
        )
        queryset = _scope_assignments(queryset, request.user)

        subject_id = request.query_params.get('subject')
        teacher_id = request.query_params.get('teacher')
        status = request.query_params.get('status')
        semester = request.query_params.get('semester')

        if subject_id:
            queryset = queryset.filter(subject_id=subject_id)
        if teacher_id:
            queryset = queryset.filter(teacher_id=teacher_id)
        if status:
            queryset = queryset.filter(status=status.upper())
        if semester:
            queryset = queryset.filter(semester=semester)

        return APIResponse.paginated(queryset, AssignmentSerializer, request)

    def post(self, request):
        if request.user.role not in ('SUPER_ADMIN', 'ADMIN', 'HOD', 'TEACHER'):
            return APIResponse.error(message='Access denied.', status=403)

        serializer = AssignmentWriteSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return APIResponse.error(message='Invalid input.', errors=serializer.errors)

        validated = serializer.validated_data
        if request.user.role != 'SUPER_ADMIN':
            if validated['teacher'].college_id != request.user.college_id:
                return APIResponse.error(message='Invalid teacher for your college.', status=403)
            if request.user.role == 'HOD' and validated['department'].id != request.user.department_id:
                return APIResponse.error(message='Invalid department.', status=403)

        assignment = serializer.save()
        return APIResponse.success(
            data=AssignmentSerializer(assignment).data,
            message='Assignment created.',
            status=201,
        )


class AssignmentDetailView(BaseAPIView):
    allowed_roles = ['SUPER_ADMIN', 'ADMIN', 'HOD', 'TEACHER', 'STUDENT']

    def get(self, request, pk):
        try:
            assignment = Assignment.objects.select_related(
                'subject', 'teacher', 'teacher__user', 'department'
            ).get(pk=pk, is_deleted=False)
        except Assignment.DoesNotExist:
            return APIResponse.error(message='Assignment not found.', status=404)

        scoped = _scope_assignments(
            Assignment.objects.filter(pk=pk), request.user
        )
        if not scoped.exists():
            return APIResponse.error(message='Access denied.', status=403)

        return APIResponse.success(data=AssignmentSerializer(assignment).data)

    def patch(self, request, pk):
        if request.user.role not in ('SUPER_ADMIN', 'ADMIN', 'HOD', 'TEACHER'):
            return APIResponse.error(message='Access denied.', status=403)
        try:
            assignment = Assignment.objects.get(pk=pk, is_deleted=False)
        except Assignment.DoesNotExist:
            return APIResponse.error(message='Assignment not found.', status=404)

        if request.user.role == 'TEACHER' and assignment.teacher.user_id != request.user.id:
            return APIResponse.error(message='You can only edit your own assignments.', status=403)

        serializer = AssignmentWriteSerializer(
            assignment, data=request.data, partial=True, context={'request': request}
        )
        if not serializer.is_valid():
            return APIResponse.error(message='Invalid input.', errors=serializer.errors)
        serializer.save()
        return APIResponse.success(data=AssignmentSerializer(assignment).data, message='Assignment updated.')

    def delete(self, request, pk):
        if request.user.role not in ('SUPER_ADMIN', 'ADMIN', 'HOD', 'TEACHER'):
            return APIResponse.error(message='Access denied.', status=403)
        try:
            assignment = Assignment.objects.get(pk=pk, is_deleted=False)
        except Assignment.DoesNotExist:
            return APIResponse.error(message='Assignment not found.', status=404)

        if request.user.role == 'TEACHER' and assignment.teacher.user_id != request.user.id:
            return APIResponse.error(message='You can only delete your own assignments.', status=403)

        assignment.is_deleted = True
        assignment.save(update_fields=['is_deleted'])
        return APIResponse.success(message='Assignment deleted.')


class AssignmentSubmissionListView(BaseAPIView):
    allowed_roles = ['SUPER_ADMIN', 'ADMIN', 'HOD', 'TEACHER', 'STUDENT', 'PARENT']

    def get(self, request):
        queryset = AssignmentSubmission.objects.filter(is_deleted=False).select_related(
            'assignment', 'student', 'graded_by',
        )
        queryset = _scope_submissions(queryset, request.user)

        assignment_id = request.query_params.get('assignment')
        student_id = request.query_params.get('student')
        status = request.query_params.get('status')

        if assignment_id:
            queryset = queryset.filter(assignment_id=assignment_id)
        if student_id:
            queryset = queryset.filter(student_id=student_id)
        if status:
            queryset = queryset.filter(status=status.upper())

        return APIResponse.paginated(queryset, AssignmentSubmissionSerializer, request)

    def post(self, request):
        """Student submits an assignment."""
        if request.user.role != 'STUDENT':
            return APIResponse.error(message='Only students can submit assignments.', status=403)

        try:
            student = Student.objects.get(user=request.user)
        except Student.DoesNotExist:
            return APIResponse.error(message='Student profile not found.', status=404)

        assignment_id = request.data.get('assignment')
        if not assignment_id:
            return APIResponse.error(message='assignment field is required.')

        try:
            assignment = Assignment.objects.get(
                pk=assignment_id, is_deleted=False,
                college=request.user.college, status='PUBLISHED', is_active=True,
            )
        except Assignment.DoesNotExist:
            return APIResponse.error(message='Assignment not found or not available.', status=404)

        now = timezone.now()
        is_late = now > assignment.due_date

        submission, created = AssignmentSubmission.objects.get_or_create(
            assignment=assignment,
            student=student,
            defaults={
                'college': request.user.college,
                'status': 'LATE' if is_late else 'SUBMITTED',
                'submitted_at': now,
                'submission_text': request.data.get('submission_text', ''),
                'attachment': request.data.get('attachment', ''),
            },
        )

        if not created:
            if submission.status == 'GRADED':
                return APIResponse.error(message='Already graded. Cannot resubmit.', status=400)
            submission.submission_text = request.data.get('submission_text', submission.submission_text)
            submission.attachment = request.data.get('attachment', submission.attachment)
            submission.submitted_at = now
            submission.status = 'LATE' if is_late else 'SUBMITTED'
            submission.save()

        return APIResponse.success(
            data=AssignmentSubmissionSerializer(submission).data,
            message='Submitted successfully.' + (' (Late submission)' if is_late else ''),
            status=201 if created else 200,
        )


class AssignmentGradeView(BaseAPIView):
    """S13 — Teacher grades a submission."""
    allowed_roles = ['SUPER_ADMIN', 'ADMIN', 'HOD', 'TEACHER']

    def patch(self, request, pk):
        try:
            submission = AssignmentSubmission.objects.select_related(
                'assignment', 'assignment__teacher', 'student'
            ).get(pk=pk, is_deleted=False)
        except AssignmentSubmission.DoesNotExist:
            return APIResponse.error(message='Submission not found.', status=404)

        if request.user.role == 'TEACHER':
            if submission.assignment.teacher.user_id != request.user.id:
                return APIResponse.error(message='You can only grade your own assignments.', status=403)

        marks = request.data.get('marks_obtained')
        feedback = request.data.get('feedback', '')

        if marks is None:
            return APIResponse.error(message='marks_obtained is required.')

        try:
            marks = int(marks)
        except (ValueError, TypeError):
            return APIResponse.error(message='marks_obtained must be an integer.')

        if marks < 0 or marks > submission.assignment.max_marks:
            return APIResponse.error(
                message=f'marks_obtained must be between 0 and {submission.assignment.max_marks}.'
            )

        from apps.teachers.models import Teacher
        try:
            teacher = Teacher.objects.get(user=request.user)
        except Teacher.DoesNotExist:
            teacher = None

        submission.marks_obtained = marks
        submission.feedback = feedback
        submission.status = 'GRADED'
        submission.graded_by = teacher
        submission.graded_at = timezone.now()
        submission.save()

        return APIResponse.success(
            data=AssignmentSubmissionSerializer(submission).data,
            message='Submission graded successfully.',
        )


class AssignmentAttachmentUploadView(BaseAPIView):
    """Upload assignment file to MinIO, return URL."""
    allowed_roles = ['SUPER_ADMIN', 'ADMIN', 'HOD', 'TEACHER', 'STUDENT']

    def post(self, request):
        file = request.FILES.get('file')
        if not file:
            return APIResponse.error(message='file is required.')

        allowed_types = [
            'application/pdf',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'image/jpeg', 'image/png',
            'video/mp4', 'video/mpeg',
            'application/zip',
        ]
        if file.content_type not in allowed_types:
            return APIResponse.error(message='File type not allowed.')

        max_size = 50 * 1024 * 1024  # 50MB
        if file.size > max_size:
            return APIResponse.error(message='File size must be under 50MB.')

        storage = MinIOStorage()
        ext = file.name.rsplit('.', 1)[-1] if '.' in file.name else 'bin'
        filename = f"assignments/{request.user.college_id}/{uuid.uuid4().hex}.{ext}"
        saved_name = storage.save(filename, file)
        url = storage.url(saved_name)

        return APIResponse.success(
            data={'url': url, 'filename': saved_name},
            message='File uploaded successfully.',
            status=201,
        )
