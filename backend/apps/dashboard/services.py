from __future__ import annotations

import calendar
import datetime
from typing import Any

from django.db.models import Count, Sum
from django.utils import timezone

from apps.core.services import CacheService


def _college_id(college) -> str:
    return str(college.id) if college else 'global'


def _month_range(months: int = 12) -> list[tuple[int, int, str]]:
    today = timezone.localdate()
    result = []
    year, month = today.year, today.month
    for _ in range(months):
        label = calendar.month_abbr[month]
        result.append((year, month, f'{label} {year}'))
        month -= 1
        if month < 1:
            month = 12
            year -= 1
    return list(reversed(result))


class DashboardService:
    CACHE_TTL = 300

    @classmethod
    def cache_key(cls, scope: str, college_id: str) -> str:
        return f'dashboard:{scope}:{college_id}'

    @classmethod
    def get_cached(cls, scope: str, college) -> dict[str, Any] | None:
        return CacheService.get(cls.cache_key(scope, _college_id(college)))

    @classmethod
    def set_cached(cls, scope: str, college, payload: dict[str, Any]) -> None:
        CacheService.set(cls.cache_key(scope, _college_id(college)), payload, cls.CACHE_TTL)

    @classmethod
    def build_super_admin_payload(cls, college) -> dict[str, Any]:
        from apps.admissions.models import AdmissionApplication
        from apps.attendance.models import Attendance
        from apps.finance.models import FeePayment
        from apps.students.models import Student
        from apps.teachers.models import Teacher

        today = timezone.localdate()
        student_qs = Student.objects.filter(is_deleted=False)
        teacher_qs = Teacher.objects.filter(is_deleted=False)
        fee_qs = FeePayment.objects.filter(is_deleted=False)
        admission_qs = AdmissionApplication.objects.filter(is_deleted=False)
        attendance_qs = Attendance.objects.filter(date=today)

        if college:
            student_qs = student_qs.filter(college=college)
            teacher_qs = teacher_qs.filter(college=college)
            fee_qs = fee_qs.filter(college=college)
            admission_qs = admission_qs.filter(college=college)
            attendance_qs = attendance_qs.filter(college=college)

        kpis = {
            'total_students': student_qs.count(),
            'total_teachers': teacher_qs.count(),
            'present_today': attendance_qs.filter(status='PRESENT').count(),
            'fee_collected_month': float(
                fee_qs.filter(status='PAID', paid_date__month=today.month, paid_date__year=today.year).aggregate(
                    t=Sum('amount_paid'),
                )['t']
                or 0,
            ),
            'pending_admissions': admission_qs.filter(status__in=['SUBMITTED', 'UNDER_REVIEW']).count(),
            'fee_defaulters': fee_qs.filter(status__in=['PENDING', 'OVERDUE', 'PARTIAL']).count(),
        }

        naac_radar = [
            {'criterion': 'Curricular', 'score': 82},
            {'criterion': 'Teaching', 'score': 78},
            {'criterion': 'Research', 'score': 65},
            {'criterion': 'Infrastructure', 'score': 88},
            {'criterion': 'Student Support', 'score': 74},
            {'criterion': 'Governance', 'score': 80},
            {'criterion': 'Values', 'score': 85},
        ]

        heatmap = []
        dept_stats = (
            student_qs.values('department__name')
            .annotate(count=Count('id'))
            .order_by('-count')[:8]
        )
        for row in dept_stats:
            dept = row['department__name'] or 'Unassigned'
            heatmap.append({'department': dept, 'students': row['count'], 'attendance': 72, 'results': 68})

        alerts = []
        if kpis['fee_defaulters'] > 0:
            alerts.append({
                'id': 'fee-defaulters',
                'title': 'Fee defaulters',
                'severity': 'high',
                'message': f"{kpis['fee_defaulters']} students have pending or overdue fees.",
            })
        if kpis['pending_admissions'] > 0:
            alerts.append({
                'id': 'pending-admissions',
                'title': 'Pending admissions',
                'severity': 'medium',
                'message': f"{kpis['pending_admissions']} applications await review.",
            })
        low_att = attendance_qs.count()
        if low_att:
            alerts.append({
                'id': 'attendance-today',
                'title': 'Attendance logged today',
                'severity': 'low',
                'message': f'{low_att} attendance records captured today.',
            })

        monthly_trends = []
        for year, month, label in _month_range(12):
            monthly_trends.append({
                'month': label,
                'fees_collected': float(
                    fee_qs.filter(status='PAID', paid_date__year=year, paid_date__month=month).aggregate(
                        t=Sum('amount_paid'),
                    )['t']
                    or 0,
                ),
                'admissions': admission_qs.filter(
                    created_at__year=year,
                    created_at__month=month,
                ).count(),
                'enrollments': admission_qs.filter(
                    status='ENROLLED',
                    updated_at__year=year,
                    updated_at__month=month,
                ).count(),
            })

        fee_by_status = {
            row['status']: row['count']
            for row in fee_qs.values('status').annotate(count=Count('id'))
        }

        return {
            'kpis': kpis,
            'naac_radar': naac_radar,
            'heatmap': heatmap,
            'alerts': alerts,
            'monthly_trends': monthly_trends,
            'fee_by_status': fee_by_status,
            'generated_at': timezone.now().isoformat(),
        }

    @classmethod
    def build_principal_payload(cls, college) -> dict[str, Any]:
        from apps.governance.models import ApprovalRequest, Meeting

        base = cls.build_super_admin_payload(college)
        meeting_qs = Meeting.objects.filter(is_deleted=False)
        approval_qs = ApprovalRequest.objects.filter(is_deleted=False)
        if college:
            meeting_qs = meeting_qs.filter(college=college)
            approval_qs = approval_qs.filter(college=college)

        base['governance'] = {
            'pending_approvals': approval_qs.filter(status='pending').count(),
            'upcoming_meetings': meeting_qs.filter(
                scheduled_at__gte=timezone.now(),
                status='scheduled',
            ).count(),
            'meetings_this_month': meeting_qs.filter(
                scheduled_at__month=timezone.localdate().month,
            ).count(),
        }
        return base

    @classmethod
    def get_super_admin(cls, college, *, use_cache: bool = True) -> dict[str, Any]:
        if use_cache:
            cached = cls.get_cached('super_admin', college)
            if cached:
                cached['from_cache'] = True
                return cached
        payload = cls.build_super_admin_payload(college)
        cls.set_cached('super_admin', college, payload)
        payload['from_cache'] = False
        return payload

    @classmethod
    def get_principal(cls, college, *, use_cache: bool = True) -> dict[str, Any]:
        if use_cache:
            cached = cls.get_cached('principal', college)
            if cached:
                cached['from_cache'] = True
                return cached
        payload = cls.build_principal_payload(college)
        cls.set_cached('principal', college, payload)
        payload['from_cache'] = False
        return payload
