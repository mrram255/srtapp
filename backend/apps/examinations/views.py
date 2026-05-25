import random
from decimal import Decimal
from django.utils import timezone
from django.db import transaction

from apps.core.responses import APIResponse
from apps.core.views import BaseAPIView
from .models import ExamSchedule, ExamResult, MCQQuestion, ExamAttempt, StudentAnswer, AdmitCard
from .serializers import (
    ExamScheduleSerializer, ExamResultSerializer, MCQQuestionSerializer,
    MCQQuestionWithAnswerSerializer, ExamAttemptSerializer,
    StudentAnswerSerializer, AdmitCardSerializer, ScorecardSerializer,
)


def _get_student(user):
    try:
        return user.student_profile
    except Exception:
        return None


class ExamScheduleListView(BaseAPIView):
    allowed_roles = ['SUPER_ADMIN', 'ADMIN', 'HOD', 'TEACHER', 'STUDENT']

    def get(self, request):
        queryset = ExamSchedule.objects.filter(is_deleted=False, is_active=True).select_related(
            'subject', 'department'
        )
        user = request.user
        if user.role == 'SUPER_ADMIN':
            pass
        elif user.role == 'STUDENT':
            student = _get_student(user)
            if not student:
                return APIResponse.error(message='Student profile not found.', status=404)
            queryset = queryset.filter(
                college=student.college,
                semester=student.semester,
            )
        else:
            if user.college_id:
                queryset = queryset.filter(college_id=user.college_id)

        exam_type = request.query_params.get('exam_type')
        subject = request.query_params.get('subject')
        semester = request.query_params.get('semester')

        if exam_type:
            queryset = queryset.filter(exam_type=exam_type)
        if subject:
            queryset = queryset.filter(subject_id=subject)
        if semester:
            queryset = queryset.filter(semester=semester)

        return APIResponse.paginated(queryset, ExamScheduleSerializer, request)

    def post(self, request):
        if request.user.role not in ('SUPER_ADMIN', 'ADMIN', 'HOD', 'TEACHER'):
            return APIResponse.error(message='Access denied.', status=403)

        serializer = ExamScheduleSerializer(data=request.data)
        if not serializer.is_valid():
            return APIResponse.error(message='Invalid input.', errors=serializer.errors)

        college = serializer.validated_data['subject'].college
        exam = serializer.save(college=college)
        return APIResponse.success(
            data=ExamScheduleSerializer(exam).data,
            message='Exam scheduled.',
            status=201,
        )


class ExamScheduleDetailView(BaseAPIView):
    allowed_roles = ['SUPER_ADMIN', 'ADMIN', 'HOD', 'TEACHER']

    def _get_exam(self, pk, user):
        try:
            exam = ExamSchedule.objects.get(pk=pk, is_deleted=False)
        except ExamSchedule.DoesNotExist:
            return None
        if user.role != 'SUPER_ADMIN' and exam.college_id != user.college_id:
            return None
        return exam

    def put(self, request, pk):
        exam = self._get_exam(pk, request.user)
        if not exam:
            return APIResponse.error(message='Not found.', status=404)
        serializer = ExamScheduleSerializer(exam, data=request.data, partial=True)
        if not serializer.is_valid():
            return APIResponse.error(message='Invalid input.', errors=serializer.errors)
        updated = serializer.save()
        return APIResponse.success(data=ExamScheduleSerializer(updated).data)

    def delete(self, request, pk):
        exam = self._get_exam(pk, request.user)
        if not exam:
            return APIResponse.error(message='Not found.', status=404)
        exam.is_deleted = True
        exam.save(update_fields=['is_deleted'])
        return APIResponse.success(message='Exam deleted.')


class MCQQuestionView(BaseAPIView):
    allowed_roles = ['SUPER_ADMIN', 'ADMIN', 'HOD', 'TEACHER']

    def get(self, request, exam_id):
        questions = MCQQuestion.objects.filter(
            exam_id=exam_id, is_deleted=False
        ).order_by('order')
        return APIResponse.success(data=MCQQuestionWithAnswerSerializer(questions, many=True).data)

    def post(self, request, exam_id):
        try:
            exam = ExamSchedule.objects.get(pk=exam_id, is_deleted=False)
        except ExamSchedule.DoesNotExist:
            return APIResponse.error(message='Exam not found.', status=404)

        if request.user.role != 'SUPER_ADMIN' and exam.college_id != request.user.college_id:
            return APIResponse.error(message='Access denied.', status=403)

        rows = request.data if isinstance(request.data, list) else [request.data]
        created = []
        errors = []

        with transaction.atomic():
            for i, row in enumerate(rows):
                row['exam'] = str(exam_id)
                row['college'] = str(exam.college_id)
                serializer = MCQQuestionSerializer(data=row)
                if not serializer.is_valid():
                    errors.append({'index': i, 'errors': serializer.errors})
                    continue
                q = serializer.save(college=exam.college)
                created.append(MCQQuestionWithAnswerSerializer(q).data)

        return APIResponse.success(
            data={'created': created, 'errors': errors},
            message=f'{len(created)} questions added.',
            status=201,
        )


class ExamStartView(BaseAPIView):
    """Student starts exam — creates attempt, shuffles questions."""
    allowed_roles = ['STUDENT']

    def post(self, request, exam_id):
        student = _get_student(request.user)
        if not student:
            return APIResponse.error(message='Student profile not found.', status=404)

        try:
            exam = ExamSchedule.objects.get(pk=exam_id, is_deleted=False, is_active=True)
        except ExamSchedule.DoesNotExist:
            return APIResponse.error(message='Exam not found.', status=404)

        # Check already attempted
        if ExamAttempt.objects.filter(exam=exam, student=student).exists():
            return APIResponse.error(message='You have already attempted this exam.', status=400)

        # Check exam timing
        now = timezone.now()
        exam_start = timezone.make_aware(
            timezone.datetime.combine(exam.exam_date, exam.start_time)
        )
        exam_end = timezone.make_aware(
            timezone.datetime.combine(exam.exam_date, exam.end_time)
        )
        if now < exam_start:
            return APIResponse.error(message='Exam has not started yet.', status=400)
        if now > exam_end:
            return APIResponse.error(message='Exam has ended.', status=400)

        # Get questions and shuffle
        questions = list(MCQQuestion.objects.filter(
            exam=exam, is_deleted=False
        ).values_list('id', flat=True))

        if not questions:
            return APIResponse.error(message='No questions found for this exam.', status=400)

        random.shuffle(questions)
        question_order = [str(q) for q in questions]

        attempt = ExamAttempt.objects.create(
            exam=exam,
            student=student,
            college=student.college,
            question_order=question_order,
            status='IN_PROGRESS',
        )

        # Return questions WITHOUT correct answers
        ordered_questions = sorted(
            MCQQuestion.objects.filter(exam=exam, is_deleted=False),
            key=lambda q: question_order.index(str(q.id))
        )

        return APIResponse.success(
            data={
                'attempt_id': str(attempt.id),
                'exam_name': exam.name,
                'duration_minutes': exam.duration_minutes,
                'total_questions': len(questions),
                'max_marks': exam.max_marks,
                'questions': MCQQuestionSerializer(ordered_questions, many=True).data,
            },
            message='Exam started. Good luck!',
            status=201,
        )


class ExamSubmitView(BaseAPIView):
    """Student submits exam — auto-grade + instant scorecard."""
    allowed_roles = ['STUDENT']

    def post(self, request, attempt_id):
        student = _get_student(request.user)
        if not student:
            return APIResponse.error(message='Student profile not found.', status=404)

        try:
            attempt = ExamAttempt.objects.select_related('exam').get(
                pk=attempt_id, student=student, is_deleted=False
            )
        except ExamAttempt.DoesNotExist:
            return APIResponse.error(message='Attempt not found.', status=404)

        if attempt.status != 'IN_PROGRESS':
            return APIResponse.error(message='Exam already submitted.', status=400)

        answers_data = request.data.get('answers', [])

        with transaction.atomic():
            # Save all answers
            for ans in answers_data:
                question_id = ans.get('question')
                selected = ans.get('selected_option')
                if not question_id:
                    continue
                try:
                    question = MCQQuestion.objects.get(pk=question_id, exam=attempt.exam)
                except MCQQuestion.DoesNotExist:
                    continue
                StudentAnswer.objects.update_or_create(
                    attempt=attempt,
                    question=question,
                    defaults={
                        'selected_option': selected,
                        'college': attempt.college,
                    },
                )

            # Calculate score
            all_answers = StudentAnswer.objects.filter(attempt=attempt).select_related('question')
            total_questions = MCQQuestion.objects.filter(exam=attempt.exam, is_deleted=False).count()
            attempted = all_answers.filter(selected_option__isnull=False).count()
            correct = all_answers.filter(is_correct=True).count()
            incorrect = all_answers.filter(is_correct=False, selected_option__isnull=False).count()
            skipped = total_questions - attempted

            marks = sum(a.marks_awarded for a in all_answers)
            marks = max(Decimal('0'), marks)
            percentage = (marks / attempt.exam.max_marks * 100) if attempt.exam.max_marks else 0
            status = 'PASS' if marks >= attempt.exam.passing_marks else 'FAIL'

            # Update attempt
            attempt.status = 'SUBMITTED'
            attempt.submitted_at = timezone.now()
            attempt.save()

            # Save to ExamResult
            result, _ = ExamResult.objects.update_or_create(
                exam=attempt.exam,
                student=student,
                defaults={
                    'college': attempt.college,
                    'marks_obtained': marks,
                    'percentage': percentage,
                    'status': status,
                },
            )

            # Calculate rank
            rank = ExamResult.objects.filter(
                exam=attempt.exam,
                is_deleted=False,
                percentage__gt=percentage,
            ).count() + 1

            total_students = ExamResult.objects.filter(
                exam=attempt.exam, is_deleted=False
            ).count()

        scorecard = {
            'exam_name': attempt.exam.name,
            'subject_name': attempt.exam.subject.name,
            'total_questions': total_questions,
            'attempted': attempted,
            'correct': correct,
            'incorrect': incorrect,
            'skipped': skipped,
            'marks_obtained': marks,
            'max_marks': attempt.exam.max_marks,
            'percentage': round(float(percentage), 2),
            'status': status,
            'rank': rank,
            'total_students': total_students,
            'answers': StudentAnswerSerializer(all_answers, many=True).data,
        }

        return APIResponse.success(data=scorecard, message='Exam submitted successfully!')


class TabSwitchView(BaseAPIView):
    """Log tab switch — anti-cheat."""
    allowed_roles = ['STUDENT']

    def post(self, request, attempt_id):
        student = _get_student(request.user)
        try:
            attempt = ExamAttempt.objects.get(
                pk=attempt_id, student=student, status='IN_PROGRESS'
            )
        except ExamAttempt.DoesNotExist:
            return APIResponse.error(message='Active attempt not found.', status=404)

        attempt.tab_switch_count += 1
        if attempt.tab_switch_count >= 3:
            attempt.status = 'DISQUALIFIED'
        attempt.save(update_fields=['tab_switch_count', 'status'])

        return APIResponse.success(
            data={
                'tab_switch_count': attempt.tab_switch_count,
                'disqualified': attempt.status == 'DISQUALIFIED',
            },
            message='Tab switch logged.',
        )


class ExamResultListView(BaseAPIView):
    allowed_roles = ['SUPER_ADMIN', 'ADMIN', 'HOD', 'TEACHER', 'STUDENT']

    def get(self, request):
        queryset = ExamResult.objects.filter(is_deleted=False).select_related(
            'exam', 'student', 'student__user'
        )
        user = request.user
        if user.role == 'STUDENT':
            student = _get_student(user)
            if not student:
                return APIResponse.error(message='Student profile not found.', status=404)
            queryset = queryset.filter(student=student)
        elif user.role != 'SUPER_ADMIN':
            queryset = queryset.filter(college_id=user.college_id)

        exam_id = request.query_params.get('exam')
        if exam_id:
            queryset = queryset.filter(exam_id=exam_id)

        return APIResponse.paginated(queryset, ExamResultSerializer, request)


class ExamRankingView(BaseAPIView):
    """Class ranking for an exam."""
    allowed_roles = ['SUPER_ADMIN', 'ADMIN', 'HOD', 'TEACHER', 'STUDENT']

    def get(self, request, exam_id):
        results = ExamResult.objects.filter(
            exam_id=exam_id,
            is_deleted=False,
        ).select_related('student', 'student__user').order_by('-percentage', '-marks_obtained')

        data = []
        for rank, result in enumerate(results, 1):
            data.append({
                'rank': rank,
                'student_name': result.student.user.full_name,
                'enrollment_number': result.student.enrollment_number,
                'marks_obtained': float(result.marks_obtained),
                'percentage': float(result.percentage or 0),
                'status': result.status,
            })

        return APIResponse.success(data=data)


class AdmitCardView(BaseAPIView):
    allowed_roles = ['SUPER_ADMIN', 'ADMIN', 'HOD', 'STUDENT']

    def get(self, request):
        user = request.user
        if user.role == 'STUDENT':
            student = _get_student(user)
            if not student:
                return APIResponse.error(message='Student profile not found.', status=404)
            queryset = AdmitCard.objects.filter(
                student=student, is_issued=True, is_deleted=False
            ).select_related('exam', 'student', 'student__user')
        else:
            queryset = AdmitCard.objects.filter(
                is_deleted=False, college_id=user.college_id
            ).select_related('exam', 'student', 'student__user')

        exam_id = request.query_params.get('exam')
        if exam_id:
            queryset = queryset.filter(exam_id=exam_id)

        return APIResponse.paginated(queryset, AdmitCardSerializer, request)

    def post(self, request):
        """Bulk issue admit cards for an exam."""
        if request.user.role not in ('SUPER_ADMIN', 'ADMIN', 'HOD'):
            return APIResponse.error(message='Access denied.', status=403)

        exam_id = request.data.get('exam')
        if not exam_id:
            return APIResponse.error(message='exam field required.')

        try:
            exam = ExamSchedule.objects.get(pk=exam_id, is_deleted=False)
        except ExamSchedule.DoesNotExist:
            return APIResponse.error(message='Exam not found.', status=404)

        from apps.students.models import Student
        students = Student.objects.filter(
            college=exam.college,
            semester=exam.semester,
            is_deleted=False,
            is_active=True,
        )
        if exam.section:
            students = students.filter(section__iexact=exam.section)

        created = 0
        for i, student in enumerate(students, 1):
            _, made = AdmitCard.objects.get_or_create(
                exam=exam,
                student=student,
                defaults={
                    'college': exam.college,
                    'roll_number': student.roll_number,
                    'seat_number': f'{exam.room_number}-{i:03d}' if exam.room_number else f'{i:03d}',
                    'is_issued': True,
                    'issued_at': timezone.now(),
                },
            )
            if made:
                created += 1

        return APIResponse.success(
            data={'issued': created},
            message=f'{created} admit cards issued.',
            status=201,
        )
