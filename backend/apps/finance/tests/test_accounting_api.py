import pytest
from rest_framework import status

from apps.finance.models import Budget, ChartOfAccount, JournalEntry, Vendor


@pytest.mark.django_db
def test_create_chart_of_account(api_client, accountant_user):
    api_client.force_authenticate(user=accountant_user)
    r = api_client.post(
        '/api/v1/finance/accounting/accounts/',
        {'code': '1001', 'name': 'Cash', 'account_type': 'asset'},
        format='json',
    )
    assert r.status_code == status.HTTP_201_CREATED
    assert r.data['data']['code'] == '1001'


@pytest.mark.django_db
def test_list_chart_of_accounts(api_client, accountant_user, college):
    ChartOfAccount.objects.create(college=college, code='2001', name='Bank', account_type='asset')
    api_client.force_authenticate(user=accountant_user)
    r = api_client.get('/api/v1/finance/accounting/accounts/')
    assert r.status_code == status.HTTP_200_OK
    assert len(r.data['data']) >= 1


@pytest.mark.django_db
def test_post_journal_entry(api_client, accountant_user, college):
    a1 = ChartOfAccount.objects.create(college=college, code='1001', name='Cash', account_type='asset')
    a2 = ChartOfAccount.objects.create(college=college, code='4001', name='Fees', account_type='income')
    api_client.force_authenticate(user=accountant_user)
    r = api_client.post(
        '/api/v1/finance/accounting/journal/',
        {
            'entry_date': '2026-05-01',
            'description': 'Fee collection',
            'lines': [
                {'account': str(a1.id), 'debit': '1000', 'credit': '0'},
                {'account': str(a2.id), 'debit': '0', 'credit': '1000'},
            ],
        },
        format='json',
    )
    assert r.status_code == status.HTTP_201_CREATED
    assert JournalEntry.objects.filter(college=college).exists()


@pytest.mark.django_db
def test_journal_rejects_imbalance(api_client, accountant_user, college):
    a1 = ChartOfAccount.objects.create(college=college, code='1002', name='Cash2', account_type='asset')
    api_client.force_authenticate(user=accountant_user)
    r = api_client.post(
        '/api/v1/finance/accounting/journal/',
        {
            'entry_date': '2026-05-01',
            'description': 'Bad',
            'lines': [{'account': str(a1.id), 'debit': '100', 'credit': '0'}],
        },
        format='json',
    )
    assert r.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_create_vendor(api_client, accountant_user):
    api_client.force_authenticate(user=accountant_user)
    r = api_client.post(
        '/api/v1/finance/accounting/vendors/',
        {'name': 'Lab Supplies Co', 'email': 'vendor@college.edu'},
        format='json',
    )
    assert r.status_code == status.HTTP_201_CREATED
    assert Vendor.objects.filter(name='Lab Supplies Co').exists()


@pytest.mark.django_db
def test_list_budgets(api_client, accountant_user, college):
    account = ChartOfAccount.objects.create(college=college, code='5001', name='Ops', account_type='expense')
    Budget.objects.create(college=college, account=account, fiscal_year='2025-26', amount_allocated=100000)
    api_client.force_authenticate(user=accountant_user)
    r = api_client.get('/api/v1/finance/accounting/budgets/')
    assert r.status_code == status.HTTP_200_OK


@pytest.mark.django_db
@pytest.mark.parametrize('account_type', ['asset', 'liability', 'equity', 'income', 'expense'])
def test_account_types(api_client, accountant_user, account_type):
    api_client.force_authenticate(user=accountant_user)
    r = api_client.post(
        '/api/v1/finance/accounting/accounts/',
        {'code': f'T{account_type[:3]}', 'name': account_type, 'account_type': account_type},
        format='json',
    )
    assert r.status_code == status.HTTP_201_CREATED
