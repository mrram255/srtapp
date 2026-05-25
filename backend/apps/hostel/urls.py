from django.urls import path

from .views import HostelAllocationListView, HostelListView, RoomListView

urlpatterns = [
    path('', HostelListView.as_view(), name='hostel_list'),
    path('rooms/', RoomListView.as_view(), name='room_list'),
    path('allocations/', HostelAllocationListView.as_view(), name='hostel_allocation_list'),
]
