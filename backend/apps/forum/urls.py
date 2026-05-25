from django.urls import path
from .views import ForumThreadListView, ForumThreadDetailView, ForumReplyListView, ForumReplyLikeView

urlpatterns = [
    path('', ForumThreadListView.as_view(), name='forum_thread_list'),
    path('<uuid:pk>/', ForumThreadDetailView.as_view(), name='forum_thread_detail'),
    path('<uuid:thread_pk>/replies/', ForumReplyListView.as_view(), name='forum_reply_list'),
    path('replies/<uuid:reply_pk>/like/', ForumReplyLikeView.as_view(), name='forum_reply_like'),
]
