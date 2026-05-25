from django.urls import path

from .views import MessFeedbackListView, MessMenuListView

urlpatterns = [
    path('', MessMenuListView.as_view(), name='mess_menu_root'),
    path('menu/', MessMenuListView.as_view(), name='mess_menu_list'),
    path('feedback/', MessFeedbackListView.as_view(), name='mess_feedback_list'),
]
