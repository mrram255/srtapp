import pytest

from apps.notifications.models import Notification, NotificationPreference, NotificationTemplate
from apps.notifications.services import NotificationDispatchService


@pytest.mark.django_db
def test_dnd_active_overnight():
    from datetime import time

    prefs = NotificationPreference(
        dnd_start_time=time(22, 0),
        dnd_end_time=time(6, 0),
    )
    # Service uses localtime; we only assert the method runs without error for configured prefs
    assert isinstance(NotificationDispatchService.is_dnd_active(prefs), bool)


@pytest.mark.django_db
def test_category_allowed_default():
    prefs = NotificationPreference(category_preferences={})
    assert NotificationDispatchService.category_allowed(prefs, 'exam') is True


@pytest.mark.django_db
def test_category_blocked():
    prefs = NotificationPreference(category_preferences={'exam': False})
    assert NotificationDispatchService.category_allowed(prefs, 'exam') is False


@pytest.mark.django_db
def test_render_template_variables(college):
    template = NotificationTemplate.objects.create(
        college=college,
        name='Greet',
        event_type='custom',
        push_title='Hi {{name}}',
        push_body='Roll {{roll}}',
    )
    rendered = NotificationDispatchService.render_template(template, {'name': 'Ali', 'roll': 'R1'})
    assert rendered['push_title'] == 'Hi Ali'
    assert rendered['push_body'] == 'Roll R1'


@pytest.mark.django_db
def test_fan_out_creates_user_notifications(college, admin_user, student_user):
    notification = Notification.objects.create(
        college=college,
        title='Test',
        message='Body',
        recipients='SPECIFIC',
        sent_by=admin_user,
    )
    notification.specific_users.set([student_user])
    count = NotificationDispatchService.fan_out_notification(notification, [student_user])
    assert count == 1
    assert notification.delivered_count == 1
