"""Handler for GET /api/v1/ — there is no default resource at the API prefix alone."""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

from apps.core.responses import APIResponse

_V1_PREFIXES = (
    'auth/',
    'colleges/',
    'students/',
    'teachers/',
    'academics/',
    'attendance/',
    'forum/',
    'analytics/',
    'study-materials/',
    'assignments/',
    'exams/',
    'finance/',
    'library/',
    'notifications/',
    'messages/',
    'admissions/',
    'hostel/',
    'transport/',
    'placements/',
    'mess/',
    'events/',
    'reports/',
    'gate/',
)


@api_view(['GET', 'HEAD'])
@permission_classes([AllowAny])
def api_v1_root(request):
    data = {
        'name': 'srtapp-api',
        'version': 1,
        'paths': [f'/api/v1/{name}' for name in _V1_PREFIXES],
        'example': '/api/v1/auth/login/',
    }
    return APIResponse.success(data=data, message='SRTAPP API v1')
