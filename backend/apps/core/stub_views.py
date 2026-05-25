from apps.core.responses import APIResponse
from apps.core.views import BaseAPIView


class StubNamespaceView(BaseAPIView):
    """Placeholder until module endpoints are implemented."""

    allowed_roles = []

    def get(self, request):
        return APIResponse.success(data=[], message='No endpoints configured yet.')
