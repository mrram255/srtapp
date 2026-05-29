import pytest
from rest_framework import status

from apps.notifications.models import Announcement, UserNotification


@pytest.mark.django_db
def test_create_announcement(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)
    response = api_client.post(
        '/api/v1/notifications/announcements/',
        data={
            'title': 'Holiday Notice',
            'content': 'College closed on Monday',
            'announcement_type': 'holiday',
            'target_audience': 'all',
        },
        format='json',
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['data']['title'] == 'Holiday Notice'


@pytest.mark.django_db
def test_list_announcements(api_client, student_user, college, admin_user):
    Announcement.objects.create(
        college=college,
        title='Pinned',
        content='Read this',
        published_by=admin_user,
        is_active=True,
    )
    api_client.force_authenticate(user=student_user)
    response = api_client.get('/api/v1/notifications/announcements/')
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['data']) >= 1


@pytest.mark.django_db
def test_publish_announcement_fans_out(api_client, admin_user, student_user, college):
    announcement = Announcement.objects.create(
        college=college,
        title='Exam schedule',
        content='Midterms next week',
        published_by=admin_user,
        target_audience='students',
    )
    api_client.force_authenticate(user=admin_user)
    response = api_client.post(f'/api/v1/notifications/announcements/{announcement.id}/publish/')
    assert response.status_code == status.HTTP_200_OK
    assert response.data['data']['published_at'] is not None
    assert UserNotification.objects.filter(user=student_user).exists()


@pytest.mark.django_db
def test_cannot_publish_twice(api_client, admin_user, college):
    from django.utils import timezone

    announcement = Announcement.objects.create(
        college=college,
        title='Once',
        content='Body',
        published_by=admin_user,
        published_at=timezone.now(),
    )
    api_client.force_authenticate(user=admin_user)
    response = api_client.post(f'/api/v1/notifications/announcements/{announcement.id}/publish/')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
