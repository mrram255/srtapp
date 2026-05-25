from celery import shared_task
from celery.utils.log import get_task_logger
from django.utils import timezone

logger = get_task_logger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_notification_task(self, notification_id: str):
    """Async notification delivery to all target users."""
    try:
        from .models import Notification, UserNotification
        from apps.accounts.models import User

        notification = Notification.objects.select_related('college').get(
            pk=notification_id, is_deleted=False
        )

        # Recipients determine karo
        recipients_type = notification.recipients
        college = notification.college

        if recipients_type == 'ALL':
            users = User.objects.filter(college=college, is_active=True, is_deleted=False)
        elif recipients_type == 'STUDENTS':
            users = User.objects.filter(college=college, role='STUDENT', is_active=True, is_deleted=False)
        elif recipients_type == 'TEACHERS':
            users = User.objects.filter(college=college, role__in=['TEACHER', 'HOD'], is_active=True, is_deleted=False)
        elif recipients_type == 'PARENTS':
            users = User.objects.filter(college=college, role='PARENT', is_active=True, is_deleted=False)
        elif recipients_type == 'ADMINS':
            users = User.objects.filter(college=college, role__in=['ADMIN', 'SUPER_ADMIN'], is_active=True, is_deleted=False)
        elif recipients_type == 'HOD':
            users = User.objects.filter(college=college, role='HOD', is_active=True, is_deleted=False)
        elif recipients_type == 'SPECIFIC':
            users = notification.specific_users.filter(is_active=True, is_deleted=False)
        else:
            users = User.objects.none()

        # Bulk UserNotification create karo
        existing = set(
            UserNotification.objects.filter(
                notification=notification
            ).values_list('user_id', flat=True)
        )

        new_notifications = []
        for user in users:
            if user.id not in existing:
                new_notifications.append(
                    UserNotification(
                        user=user,
                        notification=notification,
                        college=college,
                        is_delivered=True,
                        delivered_at=timezone.now(),
                    )
                )

        UserNotification.objects.bulk_create(new_notifications, ignore_conflicts=True)

        # Stats update karo
        total = users.count()
        notification.total_recipients = total
        notification.delivered_count = total
        notification.sent_at = timezone.now()
        notification.save(update_fields=['total_recipients', 'delivered_count', 'sent_at'])

        logger.info(f'Notification {notification_id} sent to {total} users.')
        return {'status': 'success', 'recipients': total}

    except Exception as exc:
        logger.error(f'Notification task failed: {exc}')
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=30)
def send_attendance_alert_task(self, student_id: str, subject_id: str, percentage: float):
    """75% se neeche attendance alert."""
    try:
        from .models import Notification, UserNotification
        from apps.students.models import Student
        from apps.academics.models import Subject

        student = Student.objects.select_related('user', 'college').get(pk=student_id)
        subject = Subject.objects.get(pk=subject_id)

        notification = Notification.objects.create(
            college=student.college,
            title=f'Low Attendance Alert — {subject.name}',
            message=(
                f'Dear {student.user.first_name}, your attendance in {subject.name} '
                f'is {percentage:.1f}% which is below the required 75%. '
                f'Please attend classes regularly to avoid debarment.'
            ),
            notification_type='ATTENDANCE',
            priority='HIGH',
            recipients='SPECIFIC',
            sent_by=None,
            send_push=True,
            send_email=True,
        )
        notification.specific_users.set([student.user])

        UserNotification.objects.create(
            user=student.user,
            notification=notification,
            college=student.college,
            is_delivered=True,
            delivered_at=timezone.now(),
        )

        logger.info(f'Attendance alert sent to {student.user.email}')
        return {'status': 'success', 'student': student.user.email}

    except Exception as exc:
        logger.error(f'Attendance alert task failed: {exc}')
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=30)
def send_exam_reminder_task(self, exam_id: str):
    """Exam ke 1 din pehle reminder."""
    try:
        from .models import Notification, UserNotification
        from apps.examinations.models import ExamSchedule
        from apps.accounts.models import User

        exam = ExamSchedule.objects.select_related('subject', 'college').get(pk=exam_id)

        notification = Notification.objects.create(
            college=exam.college,
            title=f'Exam Reminder — {exam.name}',
            message=(
                f'Reminder: {exam.name} for {exam.subject.name} is scheduled on '
                f'{exam.exam_date} at {exam.start_time}. '
                f'Room: {exam.room_number or "TBA"}. '
                f'Max Marks: {exam.max_marks}. All the best!'
            ),
            notification_type='EXAM',
            priority='HIGH',
            recipients='STUDENTS',
            sent_by=None,
            send_push=True,
            send_email=False,
        )

        users = User.objects.filter(
            college=exam.college,
            role='STUDENT',
            is_active=True,
            is_deleted=False,
        )

        user_notifs = [
            UserNotification(
                user=u,
                notification=notification,
                college=exam.college,
                is_delivered=True,
                delivered_at=timezone.now(),
            )
            for u in users
        ]
        UserNotification.objects.bulk_create(user_notifs, ignore_conflicts=True)

        notification.total_recipients = users.count()
        notification.delivered_count = users.count()
        notification.sent_at = timezone.now()
        notification.save(update_fields=['total_recipients', 'delivered_count', 'sent_at'])

        logger.info(f'Exam reminder sent for {exam.name}')
        return {'status': 'success', 'exam': exam.name}

    except Exception as exc:
        logger.error(f'Exam reminder task failed: {exc}')
        raise self.retry(exc=exc)
