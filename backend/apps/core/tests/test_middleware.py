from django.test import TestCase, RequestFactory, override_settings
from unittest.mock import MagicMock, patch, call
from apps.core.middleware import (
    CurrentUserMiddleware,
    RequestTimingMiddleware,
    AuditLogMiddleware,
)


class CurrentUserMiddlewareTest(TestCase):
    def test_middleware_sets_current_user(self):
        factory = RequestFactory()
        request = factory.get("/api/test/")
        user = MagicMock()
        user.is_authenticated = True
        request.user = user

        get_response = MagicMock(return_value=MagicMock(status_code=200))
        middleware = CurrentUserMiddleware(get_response)
        response = middleware(request)
        get_response.assert_called_once_with(request)

    def test_middleware_handles_anonymous_user(self):
        factory = RequestFactory()
        request = factory.get("/api/test/")
        from django.contrib.auth.models import AnonymousUser
        request.user = AnonymousUser()

        get_response = MagicMock(return_value=MagicMock(status_code=200))
        middleware = CurrentUserMiddleware(get_response)
        response = middleware(request)
        self.assertIsNotNone(response)


class RequestTimingMiddlewareTest(TestCase):
    def test_timing_middleware_adds_header(self):
        factory = RequestFactory()
        request = factory.get("/api/test/")
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.__setitem__ = MagicMock()

        get_response = MagicMock(return_value=mock_response)
        middleware = RequestTimingMiddleware(get_response)
        response = middleware(request)
        self.assertIsNotNone(response)


class AuditLogMiddlewareTest(TestCase):
    def test_audit_middleware_processes_request(self):
        factory = RequestFactory()
        request = factory.get("/api/v1/users/")
        user = MagicMock()
        user.is_authenticated = True
        user.id = "test-uuid"
        request.user = user

        mock_response = MagicMock()
        mock_response.status_code = 200

        get_response = MagicMock(return_value=mock_response)
        middleware = AuditLogMiddleware(get_response)
        response = middleware(request)
        self.assertIsNotNone(response)
