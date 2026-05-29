import pytest
from django.utils import timezone
from rest_framework import status

from apps.governance.models import ApprovalRequest, Meeting


@pytest.mark.django_db
def test_list_approvals(api_client, principal_user):
    ApprovalRequest.objects.create(
        college=principal_user.college,
        title='Leave',
        requested_by=principal_user,
    )
    api_client.force_authenticate(user=principal_user)
    r = api_client.get('/api/v1/governance/approvals/')
    assert r.status_code == status.HTTP_200_OK
    assert len(r.data['data']) >= 1


@pytest.mark.django_db
def test_create_approval(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)
    r = api_client.post(
        '/api/v1/governance/approvals/',
        {'title': 'Purchase', 'description': 'Lab equipment', 'request_type': 'purchase'},
        format='json',
    )
    assert r.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_approve_request(api_client, principal_user, admin_user):
    req = ApprovalRequest.objects.create(
        college=principal_user.college,
        title='Event',
        requested_by=admin_user,
    )
    api_client.force_authenticate(user=principal_user)
    r = api_client.post(f'/api/v1/governance/approvals/{req.id}/approve/', {'remarks': 'OK'}, format='json')
    assert r.status_code == status.HTTP_200_OK
    req.refresh_from_db()
    assert req.status == 'approved'


@pytest.mark.django_db
def test_reject_request(api_client, principal_user, admin_user):
    req = ApprovalRequest.objects.create(
        college=principal_user.college,
        title='Reject me',
        requested_by=admin_user,
    )
    api_client.force_authenticate(user=principal_user)
    r = api_client.post(f'/api/v1/governance/approvals/{req.id}/reject/')
    assert r.status_code == status.HTTP_200_OK
    req.refresh_from_db()
    assert req.status == 'rejected'


@pytest.mark.django_db
def test_meetings_alias_url(api_client, principal_user):
    api_client.force_authenticate(user=principal_user)
    r = api_client.post(
        '/api/v1/meetings/',
        {
            'title': 'Board meeting',
            'scheduled_at': timezone.now().isoformat(),
            'location': 'Hall A',
        },
        format='json',
    )
    assert r.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_list_meetings(api_client, principal_user):
    Meeting.objects.create(
        college=principal_user.college,
        title='Standup',
        scheduled_at=timezone.now(),
        organizer=principal_user,
    )
    api_client.force_authenticate(user=principal_user)
    r = api_client.get('/api/v1/meetings/')
    assert r.status_code == status.HTTP_200_OK
