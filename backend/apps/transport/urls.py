from django.urls import path

from .views import BusRouteListView, BusStopListView, TransportAllocationListView

urlpatterns = [
    path('', BusRouteListView.as_view(), name='bus_route_root'),
    path('routes/', BusRouteListView.as_view(), name='bus_route_list'),
    path('stops/', BusStopListView.as_view(), name='bus_stop_list'),
    path('allocations/', TransportAllocationListView.as_view(), name='transport_allocation_list'),
]
