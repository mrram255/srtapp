import pytest
from rest_framework import status

from apps.notifications.models import BulkNotification


@pytest.mark.django_db
def test_admin_send_bulk_to_students(api_client, admin_user, student_user):
    api_client.force_authenticate(user=admin_user)
    response = api_client.post(
        '/api/v1/notifications/send-bulk/',
        data={
            'title': 'Bulk Alert',
            'message': 'Important message for all students',
            'category': 'general',
            'target_type': 'role',
            'target_filters': {'roles': ['STUDENT']},
            'channels': {'in_app': True, 'push': True},
        },
        format='json',
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['data']['status'] in ('queued', 'completed', 'sending')


@pytest.mark.django_db
def test_bulk_history(api_client, admin_user, college):
    BulkNotification.objects.create(
        college=college,
        title='Past bulk',
        message='Done',
        target_type='all',
        channels={'in_app': True, 'push': True},
        status='completed',
        sent_count=5,
    )
    api_client.force_authenticate(user=admin_user)
    response = api_client.get('/api/v1/notifications/bulk-history/')
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['data']) >= 1


@pytest.mark.django_db
def test_bulk_individual_targets(api_client, admin_user, student_user):
    api_client.force_authenticate(user=admin_user)
    response = api_client.post(
        '/api/v1/notifications/send-bulk/',
        data={
            'title': 'Personal',
            'message': 'Just for you',
            'target_type': 'individual',
            'target_filters': {'user_ids': [str(student_user.id)]},
            'channels': {'in_app': True},
        },
        format='json',
    )
    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_student_cannot_send_bulk(api_client, student_user):
    api_client.force_authenticate(user=student_user)
    response = api_client.post(
        '/api/v1/notifications/send-bulk/',
        data={'title': 'X', 'message': 'Y', 'target_type': 'all'},
        format='json',
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
