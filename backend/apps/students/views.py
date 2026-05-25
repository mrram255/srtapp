import importlib

from django.utils import timezone

from apps.core.responses import APIResponse
from apps.core.views import BaseAPIView

from .models import Student, StudentDocument
from .serializers import (
    StudentCreateSerializer,
    StudentDashboardSerializer,
    StudentDocumentSerializer,
    StudentSelfUpdateSerializer,
    StudentSerializer,
)


def _dashboard_metrics(student):
    """Aggregate dashboard metrics when optional domain apps / models exist."""
    attendance_pct = 0.0
    pending_assignments = 0
    upcoming_exams = 0
    fee_status = 'UNKNOWN'
    recent_notifications = []

    try:
        attendance_mod = importlib.import_module('apps.attendance.models')
        Attendance = getattr(attendance_mod, 'Attendance', None)
        if Attendance is not None:
            total_classes = Attendance.objects.filter(student=student).count()
            present_classes = Attendance.objects.filter(student=student, status='PRESENT').count()
            attendance_pct = round((present_classes / total_classes * 100), 2) if total_classes else 0.0
    except Exception:
        pass

    try:
        assignments_mod = importlib.import_module('apps.assignments.models')
        AssignmentSubmission = getattr(assignments_mod, 'AssignmentSubmission', None)
        if AssignmentSubmission is not None:
            pending_assignments = AssignmentSubmission.objects.filter(student=student, status='PENDING').count()
    except Exception:
        pass

    try:
        examinations_mod = importlib.import_module('apps.examinations.models')
        ExamSchedule = getattr(examinations_mod, 'ExamSchedule', None)
        if ExamSchedule is not None:
            upcoming_exams = ExamSchedule.objects.filter(
                college=student.college,
                exam_date__gte=timezone.now().date(),
                is_deleted=False,
            ).count()
    except Exception:
        pass

    try:
        finance_mod = importlib.import_module('apps.finance.models')
        FeePayment = getattr(finance_mod, 'FeePayment', None)
        if FeePayment is not None:
            fee_status = 'PENDING'
    except Exception:
        pass

    try:
        notifications_mod = importlib.import_module('apps.notifications.models')
        Notification = getattr(notifications_mod, 'Notification', None)
        if Notification is not None:
            qs = Notification.objects.filter(college=student.college).order_by('-created_at')[:5]
            recent_notifications = [
                {
                    'title': getattr(n, 'title', ''),
                    'message': getattr(n, 'message', ''),
                    'created_at': n.created_at.isoformat(),
                }
                for n in qs
            ]
    except Exception:
        pass

    return attendance_pct, pending_assignments, upcoming_exams, fee_status, recent_notifications


class StudentListView(BaseAPIView):
    allowed_roles = ['SUPER_ADMIN', 'ADMIN', 'HOD', 'TEACHER']

    def get(self, request):
        queryset = Student.objects.filter(is_deleted=False)
        queryset = self.scope_to_role(queryset, request.user)

        department = request.query_params.get('department')
        branch = request.query_params.get('branch')
        semester = request.query_params.get('semester')
        section = request.query_params.get('section')
        batch_year = request.query_params.get('batch_year')
        is_active = request.query_params.get('is_active')

        if department:
            queryset = queryset.filter(department_id=department)
        if branch:
            queryset = queryset.filter(branch_id=branch)
        if semester:
            queryset = queryset.filter(semester=semester)
        if section:
            queryset = queryset.filter(section__iexact=section)
        if batch_year:
            queryset = queryset.filter(batch_year=batch_year)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')

        return APIResponse.paginated(queryset, StudentSerializer, request)

    def post(self, request):
        serializer = StudentCreateSerializer(data=request.data)
        if serializer.is_valid():
            if request.user.role != 'SUPER_ADMIN':
                dept = serializer.validated_data['department']
                branch = serializer.validated_data['branch']
                if dept.college_id != request.user.college_id:
                    return APIResponse.error(message='Invalid department for your college.', status=403)
                if branch.college_id != request.user.college_id:
                    return APIResponse.error(message='Invalid branch for your college.', status=403)
            student = serializer.save()
            return APIResponse.success(
                data=StudentSerializer(student).data,
                message='Student created successfully.',
                status=201,
            )
        return APIResponse.error(message='Invalid input.', errors=serializer.errors)


class StudentDetailView(BaseAPIView):
    allowed_roles = ['SUPER_ADMIN', 'ADMIN', 'HOD', 'TEACHER', 'STUDENT', 'PARENT']

    def get(self, request, pk):
        try:
            student = Student.objects.get(id=pk, is_deleted=False)

            if request.user.role == 'STUDENT' and student.user_id != request.user.id:
                return APIResponse.error(message='Access denied.', status=403)
            if request.user.role == 'PARENT':
                try:
                    wards = request.user.parent_profile.wards.all()
                except Exception:
                    wards = Student.objects.none()
                if student not in wards:
                    return APIResponse.error(message='Access denied.', status=403)
            if request.user.role in ('ADMIN', 'HOD', 'TEACHER') and student.college_id != request.user.college_id:
                return APIResponse.error(message='Access denied.', status=403)

            serializer = StudentSerializer(student)
            return APIResponse.success(data=serializer.data)
        except Student.DoesNotExist:
            return APIResponse.error(message='Student not found.', status=404)

    def patch(self, request, pk):
        try:
            student = Student.objects.get(id=pk, is_deleted=False)
            if request.user.role not in ('SUPER_ADMIN', 'ADMIN', 'HOD'):
                return APIResponse.error(message='Access denied.', status=403)
            if request.user.role in ('ADMIN', 'HOD') and student.college_id != request.user.college_id:
                return APIResponse.error(message='Access denied.', status=403)

            serializer = StudentSerializer(student, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return APIResponse.success(data=serializer.data, message='Student updated successfully.')
            return APIResponse.error(message='Invalid input.', errors=serializer.errors)
        except Student.DoesNotExist:
            return APIResponse.error(message='Student not found.', status=404)

    def delete(self, request, pk):
        try:
            student = Student.objects.get(id=pk, is_deleted=False)
            if request.user.role not in ('SUPER_ADMIN', 'ADMIN'):
                return APIResponse.error(message='Access denied.', status=403)
            if request.user.role == 'ADMIN' and student.college_id != request.user.college_id:
                return APIResponse.error(message='Access denied.', status=403)

            student.soft_delete(request.user)
            student.user.is_active = False
            student.user.save(update_fields=['is_active'])

            return APIResponse.success(message='Student deleted successfully.')
        except Student.DoesNotExist:
            return APIResponse.error(message='Student not found.', status=404)


class StudentProfileView(BaseAPIView):
    allowed_roles = ['STUDENT']

    def get(self, request):
        try:
            profile = Student.objects.get(user=request.user, is_deleted=False)
        except Student.DoesNotExist:
            return APIResponse.error(message='Student profile not found.', status=404)
        return APIResponse.success(data=StudentSerializer(profile).data)

    def patch(self, request):
        try:
            profile = Student.objects.get(user=request.user, is_deleted=False)
        except Student.DoesNotExist:
            return APIResponse.error(message='Student profile not found.', status=404)
        serializer = StudentSelfUpdateSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return APIResponse.success(data=StudentSerializer(profile).data, message='Profile updated.')
        return APIResponse.error(message='Invalid input.', errors=serializer.errors)


class StudentDashboardView(BaseAPIView):
    allowed_roles = ['STUDENT']

    def get(self, request):
        try:
            student = Student.objects.get(user=request.user, is_deleted=False)
        except Student.DoesNotExist:
            return APIResponse.error(message='Student profile not found.', status=404)

        attendance_pct, pending_assignments, upcoming_exams, fee_status, recent_notifications = _dashboard_metrics(
            student
        )

        dashboard_data = {
            'student_id': student.id,
            'name': student.full_name,
            'enrollment_number': student.enrollment_number,
            'department': student.department.name,
            'semester': student.semester,
            'section': student.section,
            'attendance_percentage': attendance_pct,
            'pending_assignments': pending_assignments,
            'upcoming_exams': upcoming_exams,
            'fee_status': fee_status,
            'recent_notifications': recent_notifications,
        }

        serializer = StudentDashboardSerializer(data=dashboard_data)
        serializer.is_valid(raise_exception=True)
        return APIResponse.success(data=serializer.validated_data)


class StudentDocumentListView(BaseAPIView):
    allowed_roles = ['SUPER_ADMIN', 'ADMIN', 'HOD', 'STUDENT']

    def get(self, request):
        queryset = StudentDocument.objects.filter(is_deleted=False)
        queryset = self.scope_to_role(queryset, request.user)

        student_id = request.query_params.get('student')
        if student_id:
            queryset = queryset.filter(student_id=student_id)

        document_type = request.query_params.get('document_type')
        if document_type:
            queryset = queryset.filter(document_type=document_type)

        is_verified = request.query_params.get('is_verified')
        if is_verified is not None:
            queryset = queryset.filter(is_verified=is_verified.lower() == 'true')

        return APIResponse.paginated(queryset, StudentDocumentSerializer, request)

    def post(self, request):
        serializer = StudentDocumentSerializer(data=request.data)
        if not serializer.is_valid():
            return APIResponse.error(message='Invalid input.', errors=serializer.errors)

        student = serializer.validated_data['student']
        college = student.college

        if request.user.role != 'SUPER_ADMIN':
            if request.user.college_id != college.id:
                return APIResponse.error(message='Access denied.', status=403)
            if request.user.role == 'STUDENT' and student.user_id != request.user.id:
                return APIResponse.error(message='Access denied.', status=403)

        serializer.validated_data['college'] = college
        doc = serializer.save(college=college)
        return APIResponse.success(
            data=StudentDocumentSerializer(doc).data,
            message='Document uploaded successfully.',
            status=201,
        )


class StudentIDCardView(BaseAPIView):
    """Get digital ID card data with QR code."""
    allowed_roles = ['SUPER_ADMIN', 'ADMIN', 'HOD', 'STUDENT']

    def get(self, request):
        from .id_card import generate_qr_base64
        from django.http import HttpResponse

        if request.user.role == 'STUDENT':
            try:
                student = request.user.student_profile
            except Exception:
                return APIResponse.error(message='Student profile not found.', status=404)
        else:
            student_id = request.query_params.get('student')
            if not student_id:
                return APIResponse.error(message='student param required.', status=400)
            try:
                from .models import Student
                student = Student.objects.select_related(
                    'user', 'college', 'department', 'branch'
                ).get(pk=student_id, is_deleted=False)
            except Exception:
                return APIResponse.error(message='Student not found.', status=404)

        # Generate QR
        qr_data = f"SRTAPP:STUDENT:{student.id}:{student.enrollment_number}"
        qr_base64 = generate_qr_base64(qr_data)

        # If PDF requested
        if request.query_params.get('format') == 'pdf':
            from .id_card import generate_id_card_pdf
            pdf_bytes = generate_id_card_pdf(student)
            response = HttpResponse(pdf_bytes, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="id_card_{student.enrollment_number}.pdf"'
            return response

        # Return JSON data
        data = {
            'student_id': str(student.id),
            'name': student.user.full_name,
            'enrollment_number': student.enrollment_number,
            'roll_number': student.roll_number,
            'department': student.department.name if student.department else '',
            'branch': student.branch.name if student.branch else '',
            'semester': student.semester,
            'section': student.section,
            'blood_group': student.blood_group,
            'college_name': student.college.name if student.college else '',
            'profile_photo': student.user.profile_photo,
            'qr_code': qr_base64,
            'valid_till': '2025-26',
        }
        return APIResponse.success(data=data)


class StudentIDVerifyView(BaseAPIView):
    """Verify student by QR scan."""
    permission_classes = []
    allowed_roles = []

    def get(self, request, student_id):
        from rest_framework.permissions import AllowAny
        self.permission_classes = [AllowAny]
        try:
            from .models import Student
            student = Student.objects.select_related(
                'user', 'college', 'department'
            ).get(pk=student_id, is_deleted=False, is_active=True)
        except Exception:
            return APIResponse.error(message='Invalid or inactive student.', status=404)

        return APIResponse.success(data={
            'valid': True,
            'name': student.user.full_name,
            'enrollment_number': student.enrollment_number,
            'department': student.department.name if student.department else '',
            'college': student.college.name if student.college else '',
            'semester': student.semester,
        })


class UniversalIDCardView(BaseAPIView):
    """Digital ID card for ALL roles."""
    allowed_roles = [
        'SUPER_ADMIN', 'ADMIN', 'HOD', 'TEACHER',
        'STUDENT', 'PARENT', 'ACCOUNTANT', 'LIBRARIAN', 'SECURITY'
    ]

    def get(self, request):
        from .id_card import generate_qr_base64, generate_id_card_pdf
        from django.http import HttpResponse

        user = request.user
        role = user.role

        ROLE_LABELS = {
            'SUPER_ADMIN': 'Super Admin',
            'ADMIN': 'Admin',
            'HOD': 'Head of Department',
            'TEACHER': 'Teacher',
            'STUDENT': 'Student',
            'PARENT': 'Parent',
            'ACCOUNTANT': 'Accountant',
            'LIBRARIAN': 'Librarian',
            'SECURITY': 'Security',
        }

        # Get role-specific ID number
        id_number = str(user.id)[:8].upper()
        department = ''
        extra = {}

        if role == 'STUDENT':
            try:
                sp = user.student_profile
                id_number = sp.enrollment_number
                department = sp.department.name if sp.department else ''
                extra = {
                    'roll_number': sp.roll_number,
                    'semester': sp.semester,
                    'section': sp.section,
                    'blood_group': sp.blood_group,
                    'branch': sp.branch.name if sp.branch else '',
                }
            except Exception:
                pass
        elif role == 'TEACHER':
            try:
                tp = user.teacher_profile
                id_number = tp.employee_id
                department = tp.department.name if tp.department else ''
                extra = {'designation': tp.designation}
            except Exception:
                pass
        elif user.department:
            department = user.department.name

        college_name = user.college.name if user.college else 'SRTAPP'
        qr_data = f"SRTAPP:{role}:{user.id}:{id_number}"
        qr_base64 = generate_qr_base64(qr_data)

        card_data = {
            'user_id': str(user.id),
            'name': user.full_name,
            'email': user.email,
            'phone': user.phone,
            'role': role,
            'role_label': ROLE_LABELS.get(role, role),
            'id_number': id_number,
            'department': department,
            'college_name': college_name,
            'profile_photo': user.profile_photo,
            'qr_code': qr_base64,
            'valid_till': '2025-26',
            **extra,
        }

        if request.query_params.get('format') == 'pdf':
            pdf_bytes = generate_id_card_pdf(card_data)
            response = HttpResponse(pdf_bytes, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="id_card_{id_number}.pdf"'
            return response

        return APIResponse.success(data=card_data)


class StudentPhotoUploadView(BaseAPIView):
    """Upload student photo — Student khud ya Admin/HOD."""
    allowed_roles = ['SUPER_ADMIN', 'ADMIN', 'HOD', 'STUDENT']

    def post(self, request):
        import os
        from django.core.files.storage import default_storage

        # Student object nikalo
        if request.user.role == 'STUDENT':
            try:
                student = request.user.student_profile
            except Exception:
                return APIResponse.error(message='Student profile not found.', status=404)
        else:
            student_id = request.data.get('student') or request.query_params.get('student')
            if not student_id:
                return APIResponse.error(message='student id required.', status=400)
            student = Student.objects.filter(pk=student_id, is_deleted=False).first()
            if not student:
                return APIResponse.error(message='Student not found.', status=404)
            # College check
            if request.user.role != 'SUPER_ADMIN' and student.college_id != request.user.college_id:
                return APIResponse.error(message='Access denied.', status=403)

        photo = request.FILES.get('photo')
        if not photo:
            return APIResponse.error(message='No file uploaded.', status=400)

        allowed_types = ['image/jpeg', 'image/png', 'image/webp']
        if photo.content_type not in allowed_types:
            return APIResponse.error(message='Only JPEG, PNG, WebP allowed.', status=400)

        if photo.size > 50 * 1024:
            return APIResponse.error(message='Photo must be under 50KB.', status=400)

        ext = os.path.splitext(photo.name)[1].lower()
        filename = f'students/photos/{student.id}{ext}'

        # Purani file delete karo agar hai
        if student.photo:
            try:
                default_storage.delete(student.photo)
            except Exception:
                pass

        saved_path = default_storage.save(filename, photo)
        student.photo = saved_path
        student.save(update_fields=['photo'])

        return APIResponse.success(
            data={'photo': saved_path},
            message='Photo uploaded successfully.',
        )


class StudentSignatureUploadView(BaseAPIView):
    """Upload student signature — Student khud ya Admin."""
    allowed_roles = ['SUPER_ADMIN', 'ADMIN', 'STUDENT']

    def post(self, request):
        import os
        from django.core.files.storage import default_storage

        if request.user.role == 'STUDENT':
            try:
                student = request.user.student_profile
            except Exception:
                return APIResponse.error(message='Student profile not found.', status=404)
        else:
            student_id = request.data.get('student') or request.query_params.get('student')
            if not student_id:
                return APIResponse.error(message='student id required.', status=400)
            student = Student.objects.filter(pk=student_id, is_deleted=False).first()
            if not student:
                return APIResponse.error(message='Student not found.', status=404)
            if request.user.role != 'SUPER_ADMIN' and student.college_id != request.user.college_id:
                return APIResponse.error(message='Access denied.', status=403)

        signature = request.FILES.get('signature')
        if not signature:
            return APIResponse.error(message='No file uploaded.', status=400)

        allowed_types = ['image/jpeg', 'image/png', 'image/webp']
        if signature.content_type not in allowed_types:
            return APIResponse.error(message='Only JPEG, PNG, WebP allowed.', status=400)

        if signature.size > 50 * 1024:
            return APIResponse.error(message='Signature must be under 50KB.', status=400)

        ext = os.path.splitext(signature.name)[1].lower()
        filename = f'students/signatures/{student.id}{ext}'

        if student.signature:
            try:
                default_storage.delete(student.signature)
            except Exception:
                pass

        saved_path = default_storage.save(filename, signature)
        student.signature = saved_path
        student.save(update_fields=['signature'])

        return APIResponse.success(
            data={'signature': saved_path},
            message='Signature uploaded successfully.',
        )
