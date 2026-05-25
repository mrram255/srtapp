from django.urls import path

from .views import MessageListView, MessageThreadListView

urlpatterns = [
    path('threads/', MessageThreadListView.as_view(), name='message_thread_list'),
    path('', MessageListView.as_view(), name='message_list'),
]
