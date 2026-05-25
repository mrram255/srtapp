from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Attendance, AttendanceSummary


@receiver(post_save, sender=Attendance)
def update_attendance_summary(sender, instance, **kwargs):
    if instance.is_deleted:
        return

    student = instance.student
    subject = instance.subject

    # Get current academic year from college
    try:
        academic_year = instance.college.academic_years.filter(
            is_current=True
        ).first()
        if not academic_year:
            return
    except Exception:
        return

    records = Attendance.objects.filter(
        student=student,
        subject=subject,
        is_deleted=False,
    )

    total = records.count()
    present = records.filter(status='PRESENT').count()
    absent = records.filter(status='ABSENT').count()
    late = records.filter(status='LATE').count()
    excused = records.filter(status='EXCUSED').count()
    percentage = round((present / total) * 100, 2) if total > 0 else 0.00

    AttendanceSummary.objects.update_or_create(
        student=student,
        subject=subject,
        academic_year=academic_year,
        defaults={
            'college': instance.college,
            'total_classes': total,
            'present_count': present,
            'absent_count': absent,
            'late_count': late,
            'excused_count': excused,
            'percentage': percentage,
            'is_deleted': False,
        },
    )
