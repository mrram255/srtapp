import pytest
from rest_framework import status

from apps.notifications.models import NotificationTemplate


@pytest.mark.django_db
def test_admin_lists_templates(api_client, admin_user, college):
    NotificationTemplate.objects.create(
        college=college,
        name='Fee Due',
        event_type='fee_due',
        email_subject='Fee due {{name}}',
        push_title='Fee',
        push_body='Pay now',
    )
    api_client.force_authenticate(user=admin_user)
    response = api_client.get('/api/v1/notifications/templates/')
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['data']) >= 1


@pytest.mark.django_db
def test_admin_creates_template(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)
    response = api_client.post(
        '/api/v1/notifications/templates/',
        data={
            'name': 'Result Published',
            'event_type': 'result_published',
            'email_subject': 'Results',
            'push_title': 'Results',
            'push_body': 'Your results are out',
        },
        format='json',
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['data']['name'] == 'Result Published'


@pytest.mark.django_db
def test_admin_updates_template(api_client, admin_user, college):
    template = NotificationTemplate.objects.create(
        college=college,
        name='Old',
        event_type='custom',
    )
    api_client.force_authenticate(user=admin_user)
    response = api_client.patch(
        f'/api/v1/notifications/templates/{template.id}/',
        data={'name': 'New Name'},
        format='json',
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data['data']['name'] == 'New Name'


@pytest.mark.django_db
def test_student_cannot_create_template(api_client, student_user):
    api_client.force_authenticate(user=student_user)
    response = api_client.post(
        '/api/v1/notifications/templates/',
        data={'name': 'X', 'event_type': 'custom'},
        format='json',
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
