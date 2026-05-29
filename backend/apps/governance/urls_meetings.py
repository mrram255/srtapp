from django.urls import path

from .views import MeetingDetailView, MeetingListView

urlpatterns = [
    path('', MeetingListView.as_view(), name='meetings_root'),
    path('<uuid:pk>/', MeetingDetailView.as_view(), name='meetings_detail'),
]
