from django.apps import apps as django_apps
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from config.health import health_check

from apps.core.api_root import api_v1_root

urlpatterns = [
    path('health/', health_check, name='health_check'),
    path('api/v1/', api_v1_root, name='api_v1_root'),
    path('api/v1/auth/', include('apps.authentication.urls')),
    path('api/v1/accounts/', include('apps.accounts.urls')),
    path('api/v1/colleges/', include('apps.colleges.urls')),
    path('api/v1/students/', include('apps.students.urls')),
    path('api/v1/teachers/', include('apps.teachers.urls')),
    path('api/v1/academics/', include('apps.academics.urls')),
    path('api/v1/attendance/', include('apps.attendance.urls')),
    path('api/v1/forum/', include('apps.forum.urls')),
    path('api/v1/analytics/', include('apps.analytics.urls')),
    path('api/v1/study-materials/', include('apps.study_materials.urls')),
    path('api/v1/assignments/', include('apps.assignments.urls')),
    path('api/v1/exams/', include('apps.examinations.urls')),
    path('api/v1/finance/', include('apps.finance.urls')),
    path('api/v1/library/', include('apps.library.urls')),
    path('api/v1/notifications/', include('apps.notifications.urls')),
    path('api/v1/messages/', include('apps.messaging.urls')),
    path('api/v1/admissions/', include('apps.admissions.urls')),
    path('api/v1/hostel/', include('apps.hostel.urls')),
    path('api/v1/transport/', include('apps.transport.urls')),
    path('api/v1/placements/', include('apps.placements.urls')),
    path('api/v1/mess/', include('apps.mess.urls')),
    path('api/v1/events/', include('apps.events.urls')),
    path('api/v1/reports/', include('apps.reports.urls')),
    path('api/v1/gate/', include('apps.gate.urls')),
    path('manage-portal/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    try:
        import debug_toolbar
    except ImportError:
        debug_toolbar = None

    if debug_toolbar is not None:
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns

if django_apps.is_installed('silk'):
    urlpatterns += [
        path('silk/', include('silk.urls', namespace='silk')),
    ]
