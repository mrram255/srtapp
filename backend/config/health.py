"""Public health endpoint for load balancers and uptime checks."""

from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    return Response(
        {
            'status': 'healthy',
            'timestamp': timezone.now().isoformat(),
            'version': '2.0.0',
        }
    )
