from celery import shared_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@shared_task
def refresh_dashboard_cache_task(college_id: str | None = None):
    from apps.colleges.models import College
    from apps.dashboard.services import DashboardService

    colleges = College.objects.filter(is_deleted=False)
    if college_id:
        colleges = colleges.filter(pk=college_id)

    refreshed = 0
    for college in colleges:
        DashboardService.get_super_admin(college, use_cache=False)
        DashboardService.get_principal(college, use_cache=False)
        refreshed += 1

    logger.info('Refreshed dashboard cache for %s colleges', refreshed)
    return {'refreshed': refreshed}
