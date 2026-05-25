from django.db.models import Avg, Count, Max, Min, Q, F
from apps.core.responses import APIResponse
from apps.core.views import BaseAPIView
from apps.examinations.models import ExamResult
from apps.attendance.models import AttendanceSummary
from apps.assignments.models import AssignmentSubmission


class StudentPerformanceView(BaseAPIView):
    """S14 — Per-student marks trend + weak subjects."""
    allowed_roles = ['SUPER_ADMIN', 'ADMIN', 'HOD', 'TEACHER', 'STUDENT', 'PARENT']

    def get(self, request):
        student_id = request.query_params.get('student')
        if not student_id:
            if request.user.role == 'STUDENT':
                try:
                    student_id = str(request.user.student_profile.id)
                except Exception:
                    return APIResponse.error(message='Student profile not found.', status=404)
            else:
                return APIResponse.error(message='student param required.', status=400)

        # Marks trend per exam
        results = ExamResult.objects.filter(
            student_id=student_id, is_deleted=False
        ).select_related('exam', 'exam__subject').order_by('exam__exam_date')

        trend = []
        subject_stats = {}

        for r in results:
            subject_name = r.exam.subject.name if r.exam.subject else 'Unknown'
            trend.append({
                'exam_id': str(r.exam_id),
                'exam_name': r.exam.name,
                'subject': subject_name,
                'exam_date': str(r.exam.exam_date),
                'marks_obtained': r.marks_obtained,
                'max_marks': r.exam.max_marks,
                'percentage': float(r.percentage),
                'status': r.status,
            })
            if subject_name not in subject_stats:
                subject_stats[subject_name] = {'total': 0, 'count': 0}
            subject_stats[subject_name]['total'] += float(r.percentage)
            subject_stats[subject_name]['count'] += 1

        # Weak subjects (avg < 50%)
        subject_averages = [
            {
                'subject': name,
                'avg_percentage': round(v['total'] / v['count'], 2),
                'exam_count': v['count'],
                'is_weak': (v['total'] / v['count']) < 50,
            }
            for name, v in subject_stats.items()
        ]
        subject_averages.sort(key=lambda x: x['avg_percentage'])
        weak_subjects = [s for s in subject_averages if s['is_weak']]

        # Attendance summary
        attendance = AttendanceSummary.objects.filter(
            student_id=student_id, is_deleted=False
        ).aggregate(
            avg_attendance=Avg('percentage'),
            subjects_below_75=Count('id', filter=Q(percentage__lt=75)),
        )

        # Assignment stats
        assignment_stats = AssignmentSubmission.objects.filter(
            student_id=student_id, is_deleted=False
        ).aggregate(
            total=Count('id'),
            submitted=Count('id', filter=Q(status__in=['SUBMITTED', 'LATE', 'GRADED'])),
            graded=Count('id', filter=Q(status='GRADED')),
            avg_marks=Avg('marks_obtained'),
        )

        overall_avg = (
            sum(r['percentage'] for r in trend) / len(trend) if trend else 0
        )

        return APIResponse.success(data={
            'student_id': student_id,
            'overall_avg_percentage': round(overall_avg, 2),
            'exam_trend': trend,
            'subject_averages': subject_averages,
            'weak_subjects': weak_subjects,
            'attendance': {
                'avg_percentage': round(float(attendance['avg_attendance'] or 0), 2),
                'subjects_below_75': attendance['subjects_below_75'],
            },
            'assignments': {
                'total': assignment_stats['total'],
                'submitted': assignment_stats['submitted'],
                'graded': assignment_stats['graded'],
                'avg_marks': round(float(assignment_stats['avg_marks'] or 0), 2),
            },
        })


class ClassAnalyticsView(BaseAPIView):
    """S14 — Class average + topper + distribution per exam."""
    allowed_roles = ['SUPER_ADMIN', 'ADMIN', 'HOD', 'TEACHER']

    def get(self, request):
        exam_id = request.query_params.get('exam')
        if not exam_id:
            return APIResponse.error(message='exam param required.', status=400)

        results = ExamResult.objects.filter(
            exam_id=exam_id, is_deleted=False
        ).select_related('student', 'student__user')

        if not results.exists():
            return APIResponse.error(message='No results found for this exam.', status=404)

        stats = results.aggregate(
            avg=Avg('percentage'),
            highest=Max('marks_obtained'),
            lowest=Min('marks_obtained'),
            total_students=Count('id'),
            passed=Count('id', filter=Q(status='PASS')),
            failed=Count('id', filter=Q(status='FAIL')),
        )

        # Score distribution buckets
        distribution = {
            'A (90-100%)': results.filter(percentage__gte=90).count(),
            'B (75-89%)':  results.filter(percentage__gte=75, percentage__lt=90).count(),
            'C (60-74%)':  results.filter(percentage__gte=60, percentage__lt=75).count(),
            'D (50-59%)':  results.filter(percentage__gte=50, percentage__lt=60).count(),
            'F (<50%)':    results.filter(percentage__lt=50).count(),
        }

        # Top 5
        toppers = results.order_by('-marks_obtained')[:5].values(
            'student__user__full_name',
            'student__enrollment_number',
            'marks_obtained',
            'percentage',
            'rank',
        )

        return APIResponse.success(data={
            'exam_id': exam_id,
            'total_students': stats['total_students'],
            'class_average': round(float(stats['avg'] or 0), 2),
            'highest_marks': stats['highest'],
            'lowest_marks': stats['lowest'],
            'pass_count': stats['passed'],
            'fail_count': stats['failed'],
            'pass_percentage': round(stats['passed'] / stats['total_students'] * 100, 2) if stats['total_students'] else 0,
            'score_distribution': distribution,
            'toppers': list(toppers),
        })


class DashboardStatsView(BaseAPIView):
    """Real dashboard stats per role."""
    allowed_roles = ['SUPER_ADMIN', 'ADMIN', 'HOD', 'TEACHER', 'STUDENT', 'ACCOUNTANT', 'LIBRARIAN', 'PARENT']

    def get(self, request):
        from apps.students.models import Student
        from apps.teachers.models import Teacher
        from apps.attendance.models import Attendance
        from apps.finance.models import FeePayment
        from apps.library.models import BookBorrowing
        from apps.assignments.models import Assignment

        user = request.user
        role = user.role
        college = getattr(user, 'college', None)
        data = {}

        if role in ('SUPER_ADMIN', 'ADMIN'):
            data = {
                'total_students': Student.objects.filter(college=college, is_deleted=False).count(),
                'total_teachers': Teacher.objects.filter(college=college, is_deleted=False).count(),
                'present_today': Attendance.objects.filter(
                    college=college, date=__import__('datetime').date.today(), status='PRESENT'
                ).count(),
                'fee_collected_month': FeePayment.objects.filter(
                    college=college, status='PAID',
                    paid_date__month=__import__('datetime').date.today().month
                ).aggregate(total=__import__('django.db.models', fromlist=['Sum']).Sum('amount_paid'))['total'] or 0,
            }
        elif role == 'HOD':
            dept = getattr(user, 'department', None)
            data = {
                'dept_students': Student.objects.filter(college=college, branch__department=dept, is_deleted=False).count(),
                'dept_teachers': Teacher.objects.filter(college=college, department=dept, is_deleted=False).count(),
                'pending_assignments': Assignment.objects.filter(college=college, department=dept, status='PUBLISHED', is_deleted=False).count(),
            }
        elif role == 'TEACHER':
            try:
                teacher = Teacher.objects.get(user=user)
                data = {
                    'my_assignments': Assignment.objects.filter(teacher=teacher, is_deleted=False).count(),
                    'pending_grading': AssignmentSubmission.objects.filter(
                        assignment__teacher=teacher, status='SUBMITTED', is_deleted=False
                    ).count(),
                    'classes_today': Attendance.objects.filter(
                        teacher=teacher, date__date=__import__('datetime').date.today()
                    ).values('subject').distinct().count(),
                }
            except Teacher.DoesNotExist:
                data = {}
        elif role == 'STUDENT':
            try:
                student = Student.objects.get(user=user)
                att = AttendanceSummary.objects.filter(student=student, is_deleted=False).aggregate(avg=Avg('percentage'))
                data = {
                    'attendance_avg': round(float(att['avg'] or 0), 2),
                    'pending_assignments': AssignmentSubmission.objects.filter(
                        student=student, status='PENDING', is_deleted=False
                    ).count(),
                    'results_count': ExamResult.objects.filter(student=student, is_deleted=False).count(),
                    'books_borrowed': BookBorrowing.objects.filter(student=student, status='BORROWED', is_deleted=False).count(),
                }
            except Student.DoesNotExist:
                data = {}
        elif role == 'ACCOUNTANT':
            from django.db.models import Sum
            import datetime
            today = datetime.date.today()
            data = {
                'collected_this_month': FeePayment.objects.filter(
                    college=college, status='PAID', paid_date__month=today.month, is_deleted=False
                ).aggregate(total=Sum('amount_paid'))['total'] or 0,
                'pending_payments': FeePayment.objects.filter(
                    college=college, status='PENDING', is_deleted=False
                ).count(),
                'total_students': Student.objects.filter(college=college, is_deleted=False).count(),
            }
        elif role == 'LIBRARIAN':
            data = {
                'books_borrowed': BookBorrowing.objects.filter(college=college, status='BORROWED', is_deleted=False).count(),
                'overdue_books': BookBorrowing.objects.filter(college=college, status='OVERDUE', is_deleted=False).count(),
            }

        return APIResponse.success(data=data)
