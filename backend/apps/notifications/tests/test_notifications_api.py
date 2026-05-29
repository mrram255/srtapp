import pytest
from rest_framework import status


@pytest.mark.django_db
def test_notification_list_requires_auth(api_client):
    response = api_client.get('/api/v1/notifications/')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_student_lists_notifications(api_client, student_user, broadcast_notification):
    api_client.force_authenticate(user=student_user)
    response = api_client.get('/api/v1/notifications/')
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['data']) >= 1
    assert response.data['data'][0]['notification']['title'] == 'Welcome'


@pytest.mark.django_db
def test_unread_count(api_client, student_user, broadcast_notification):
    api_client.force_authenticate(user=student_user)
    response = api_client.get('/api/v1/notifications/unread-count/')
    assert response.status_code == status.HTTP_200_OK
    assert response.data['data']['unread_count'] == 1


@pytest.mark.django_db
def test_mark_read(api_client, student_user, broadcast_notification):
    api_client.force_authenticate(user=student_user)
    response = api_client.post(f'/api/v1/notifications/{broadcast_notification.id}/read/')
    assert response.status_code == status.HTTP_200_OK
    count = api_client.get('/api/v1/notifications/unread-count/')
    assert count.data['data']['unread_count'] == 0


@pytest.mark.django_db
def test_mark_all_read(api_client, student_user, broadcast_notification):
    api_client.force_authenticate(user=student_user)
    response = api_client.post('/api/v1/notifications/mark-all-read/')
    assert response.status_code == status.HTTP_200_OK
    assert response.data['data']['marked_read'] >= 1


@pytest.mark.django_db
def test_filter_unread_only(api_client, student_user, broadcast_notification):
    api_client.force_authenticate(user=student_user)
    response = api_client.get('/api/v1/notifications/', {'is_read': 'false'})
    assert response.status_code == status.HTTP_200_OK
    assert all(not item['is_read'] for item in response.data['data'])


@pytest.mark.django_db
def test_admin_can_broadcast(api_client, admin_user, student_user):
    api_client.force_authenticate(user=admin_user)
    response = api_client.post(
        '/api/v1/notifications/',
        data={
            'title': 'Holiday',
            'message': 'College closed tomorrow',
            'notification_type': 'ANNOUNCEMENT',
            'category': 'general',
            'priority': 'HIGH',
            'recipients': 'STUDENTS',
            'send_push': True,
        },
        format='json',
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['data']['id']


@pytest.mark.django_db
def test_student_cannot_broadcast(api_client, student_user):
    api_client.force_authenticate(user=student_user)
    response = api_client.post(
        '/api/v1/notifications/',
        data={'title': 'X', 'message': 'Y', 'recipients': 'ALL'},
        format='json',
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
