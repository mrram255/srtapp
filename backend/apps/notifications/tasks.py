from celery import shared_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_notification_task(self, notification_id: str):
    """Async notification delivery with channel dispatch."""
    try:
        from .models import Notification
        from .services import NotificationDispatchService

        notification = Notification.objects.select_related('college').get(
            pk=notification_id,
            is_deleted=False,
        )
        delivered = NotificationDispatchService.fan_out_notification(notification)
        logger.info('Notification %s delivered to %s users.', notification_id, delivered)
        return {'status': 'success', 'delivered': delivered}
    except Exception as exc:
        logger.error('Notification task failed: %s', exc)
        raise self.retry(exc=exc) from exc


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_bulk_notification_task(self, bulk_id: str):
    try:
        from .models import BulkNotification
        from .services import NotificationDispatchService

        bulk = BulkNotification.objects.select_related('college').get(pk=bulk_id, is_deleted=False)
        bulk = NotificationDispatchService.process_bulk(bulk)
        logger.info('Bulk notification %s completed (%s sent).', bulk_id, bulk.sent_count)
        return {'status': bulk.status, 'sent_count': bulk.sent_count}
    except Exception as exc:
        logger.error('Bulk notification task failed: %s', exc)
        raise self.retry(exc=exc) from exc


@shared_task(bind=True, max_retries=3, default_retry_delay=30)
def send_attendance_alert_task(self, student_id: str, subject_id: str, percentage: float):
    """Attendance below 75% alert."""
    try:
        from django.utils import timezone

        from .models import Notification, UserNotification
        from .services import NotificationDispatchService
        from apps.academics.models import Subject
        from apps.students.models import Student

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
            category='attendance',
            priority='HIGH',
            recipients='SPECIFIC',
            send_push=True,
            send_email=True,
        )
        notification.specific_users.set([student.user])
        NotificationDispatchService.fan_out_notification(notification, [student.user])

        logger.info('Attendance alert sent to %s', student.user.email)
        return {'status': 'success', 'student': student.user.email}
    except Exception as exc:
        logger.error('Attendance alert task failed: %s', exc)
        raise self.retry(exc=exc) from exc


@shared_task(bind=True, max_retries=3, default_retry_delay=30)
def send_exam_reminder_task(self, exam_id: str):
    """Exam reminder one day before."""
    try:
        from .models import Notification
        from .services import NotificationDispatchService
        from apps.accounts.models import User
        from apps.examinations.models import ExamSchedule

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
            category='exam',
            priority='HIGH',
            recipients='STUDENTS',
            send_push=True,
        )

        users = list(
            User.objects.filter(
                college=exam.college,
                role='STUDENT',
                is_active=True,
                is_deleted=False,
            ),
        )
        NotificationDispatchService.fan_out_notification(notification, users)

        logger.info('Exam reminder sent for %s', exam.name)
        return {'status': 'success', 'exam': exam.name}
    except Exception as exc:
        logger.error('Exam reminder task failed: %s', exc)
        raise self.retry(exc=exc) from exc
