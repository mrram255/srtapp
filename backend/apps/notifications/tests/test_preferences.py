import pytest
from rest_framework import status

from apps.notifications.models import NotificationPreference


@pytest.mark.django_db
def test_preferences_created_on_get(api_client, student_user):
    api_client.force_authenticate(user=student_user)
    response = api_client.get('/api/v1/notifications/preferences/')
    assert response.status_code == status.HTTP_200_OK
    assert response.data['data']['email_enabled'] is True
    assert NotificationPreference.objects.filter(user=student_user).exists()


@pytest.mark.django_db
def test_patch_preferences(api_client, student_user):
    api_client.force_authenticate(user=student_user)
    response = api_client.patch(
        '/api/v1/notifications/preferences/',
        data={'sms_enabled': False, 'whatsapp_enabled': True},
        format='json',
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data['data']['sms_enabled'] is False
    assert response.data['data']['whatsapp_enabled'] is True


@pytest.mark.django_db
def test_category_preferences_stored(api_client, student_user):
    api_client.force_authenticate(user=student_user)
    response = api_client.patch(
        '/api/v1/notifications/preferences/',
        data={'category_preferences': {'exam': False, 'finance': True}},
        format='json',
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data['data']['category_preferences']['exam'] is False
