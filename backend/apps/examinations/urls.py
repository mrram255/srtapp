from django.urls import path
from .views import (
    ExamScheduleListView,
    ExamScheduleDetailView,
    MCQQuestionView,
    ExamStartView,
    ExamSubmitView,
    TabSwitchView,
    ExamResultListView,
    ExamRankingView,
    AdmitCardView,
)

urlpatterns = [
    path('', ExamScheduleListView.as_view(), name='exam_list'),
    path('<uuid:pk>/', ExamScheduleDetailView.as_view(), name='exam_detail'),
    path('<uuid:exam_id>/questions/', MCQQuestionView.as_view(), name='exam_questions'),
    path('<uuid:exam_id>/start/', ExamStartView.as_view(), name='exam_start'),
    path('<uuid:exam_id>/ranking/', ExamRankingView.as_view(), name='exam_ranking'),
    path('attempts/<uuid:attempt_id>/submit/', ExamSubmitView.as_view(), name='exam_submit'),
    path('attempts/<uuid:attempt_id>/tab-switch/', TabSwitchView.as_view(), name='tab_switch'),
    path('results/', ExamResultListView.as_view(), name='exam_results'),
    path('admit-cards/', AdmitCardView.as_view(), name='admit_cards'),
]
