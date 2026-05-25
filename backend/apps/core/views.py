import logging
import traceback

from django.core.exceptions import PermissionDenied
from django.http import Http404
from rest_framework.exceptions import APIException
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.core.permissions import RoleBasedPermission
from apps.core.responses import APIResponse
from apps.core.throttles import APIRateThrottle

audit_logger = logging.getLogger('audit')
security_logger = logging.getLogger('security')


class BaseAPIView(APIView):
    permission_classes = [IsAuthenticated, RoleBasedPermission]
    throttle_classes = [APIRateThrottle]
    allowed_roles = []

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        self._log_access(request)

    def _log_access(self, request):
        audit_logger.info(
            {
                'event': 'api_access',
                'user_id': str(request.user.id) if request.user.is_authenticated else 'anonymous',
                'role': getattr(request.user, 'role', 'none'),
                'college': str(getattr(request.user, 'college_id', '')),
                'path': request.path,
                'method': request.method,
                'ip': self._get_ip(request),
                'ua': request.META.get('HTTP_USER_AGENT', '')[:200],
            }
        )

    def _get_ip(self, request):
        xff = request.META.get('HTTP_X_FORWARDED_FOR')
        return xff.split(',')[0].strip() if xff else request.META.get('REMOTE_ADDR', '')

    def scope_to_role(self, queryset, user):
        """
        Scope ANY queryset to the user's role automatically.
        ALWAYS call this on every queryset returned to a user.
        """
        role = user.role
        if role == 'SUPER_ADMIN':
            return queryset
        if role in ('ADMIN', 'ACCOUNTANT', 'LIBRARIAN', 'SECURITY'):
            return queryset.filter(college=user.college)
        if role == 'HOD':
            return queryset.filter(college=user.college, department=user.department)
        if role == 'TEACHER':
            return queryset.filter(
                college=user.college,
                classes__teacher__user=user,
            )
        if role == 'STUDENT':
            return queryset.filter(college=user.college, student__user=user)
        if role == 'PARENT':
            return queryset.filter(
                college=user.college,
                student__in=user.parent_profile.wards.all(),
            )
        return queryset.none()

    def handle_exception(self, exc):
        """Delegate DRF/Django HTTP exceptions; hide unexpected errors."""
        if isinstance(exc, (APIException, Http404, PermissionDenied)):
            return super().handle_exception(exc)

        security_logger.error(
            {
                'event': 'unhandled_exception',
                'path': getattr(self.request, 'path', 'unknown'),
                'error': str(exc),
                'trace': traceback.format_exc()[-2000:],
            }
        )
        return APIResponse.error(
            message="An error occurred. Please try again.",
            status=500,
        )
