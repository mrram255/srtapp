from django.urls import path

from .views import EventListView, EventRegistrationListView

urlpatterns = [
    path('', EventListView.as_view(), name='event_list'),
    path('registrations/', EventRegistrationListView.as_view(), name='event_registration_list'),
]
