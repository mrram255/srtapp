"""
Canonical User model for the SRTAPP RBAC layer.

Django's AUTH_USER_MODEL is ``accounts.User`` (login, credentials, profile fields).
The ``users`` app owns Role/Module/RBAC; import User from here or via get_user_model().
"""

from django.contrib.auth import get_user_model

User = get_user_model()

__all__ = ['User']
