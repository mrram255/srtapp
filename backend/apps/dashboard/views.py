from apps.core.responses import APIResponse
from apps.core.views import BaseAPIView

from .services import DashboardService


class SuperAdminDashboardView(BaseAPIView):
    allowed_roles = ['SUPER_ADMIN', 'ADMIN']

    def get(self, request):
        college = request.user.college
        if request.user.role == 'SUPER_ADMIN':
            college_id = request.query_params.get('college')
            if college_id:
                from apps.colleges.models import College

                college = College.objects.filter(pk=college_id, is_deleted=False).first()

        refresh = request.query_params.get('refresh', '').lower() == 'true'
        payload = DashboardService.get_super_admin(college, use_cache=not refresh)
        return APIResponse.success(data=payload)


class PrincipalDashboardView(BaseAPIView):
    allowed_roles = ['PRINCIPAL', 'VICE_PRINCIPAL', 'DEAN', 'SUPER_ADMIN', 'ADMIN']

    def get(self, request):
        college = request.user.college
        if not college and request.user.role == 'SUPER_ADMIN':
            college_id = request.query_params.get('college')
            if college_id:
                from apps.colleges.models import College

                college = College.objects.filter(pk=college_id, is_deleted=False).first()

        if college is None:
            return APIResponse.error(message='College context required.', status=400)

        refresh = request.query_params.get('refresh', '').lower() == 'true'
        payload = DashboardService.get_principal(college, use_cache=not refresh)
        return APIResponse.success(data=payload)
