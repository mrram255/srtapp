from django.db.models import Count, Q, Avg
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import Designation, Staff, StaffServiceBook
from .serializers import (
    DesignationSerializer,
    StaffListSerializer,
    StaffDetailSerializer,
    StaffServiceBookSerializer,
)


class DesignationViewSet(viewsets.ModelViewSet):
    queryset = Designation.objects.filter(is_deleted=False).select_related('college')
    serializer_class = DesignationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'college']
    search_fields = ['name']
    ordering_fields = ['level', 'name']
    ordering = ['level']


class StaffViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['staff_type', 'designation', 'department', 'status', 'college']
    search_fields = [
        'employee_id',
        'user__first_name', 'user__last_name', 'user__email',
    ]
    ordering_fields = ['employee_id', 'date_of_joining', 'status']
    ordering = ['employee_id']

    def get_queryset(self):
        return (
            Staff.objects
            .select_related('user', 'designation', 'department', 'college')
            .filter(is_deleted=False)
        )

    def get_serializer_class(self):
        if self.action == 'list':
            return StaffListSerializer
        return StaffDetailSerializer

    @action(detail=True, methods=['get', 'post'], url_path='service-book')
    def service_book(self, request, pk=None):
        staff = self.get_object()
        if request.method == 'GET':
            entries = staff.service_book_entries.select_related(
                'old_designation', 'new_designation'
            )
            serializer = StaffServiceBookSerializer(entries, many=True)
            return Response(serializer.data)

        # POST — add new entry
        data = request.data.copy()
        data['staff'] = staff.id
        serializer = StaffServiceBookSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save(created_by=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'], url_path='statistics')
    def statistics(self, request):
        college_id = request.query_params.get('college')
        qs = Staff.objects.filter(is_deleted=False)
        if college_id:
            qs = qs.filter(college_id=college_id)

        data = {
            'total': qs.count(),
            'by_type': dict(
                qs.values_list('staff_type')
                  .annotate(c=Count('id'))
                  .values_list('staff_type', 'c')
            ),
            'by_status': dict(
                qs.values_list('status')
                  .annotate(c=Count('id'))
                  .values_list('status', 'c')
            ),
            'phd_holders': qs.filter(phd_status='completed').count(),
            'net_set_qualified': qs.filter(net_set_qualified=True).count(),
            'phd_percentage': round(
                qs.filter(phd_status='completed').count() / max(qs.count(), 1) * 100, 2
            ),
            'net_set_percentage': round(
                qs.filter(net_set_qualified=True).count() / max(qs.count(), 1) * 100, 2
            ),
        }
        return Response(data)

    @action(detail=False, methods=['get'], url_path='qualification-summary')
    def qualification_summary(self, request):
        """NAAC data: PhD %, NET/SET %."""
        college_id = request.query_params.get('college')
        qs = Staff.objects.filter(is_deleted=False, staff_type='teaching')
        if college_id:
            qs = qs.filter(college_id=college_id)

        total = qs.count()
        data = {
            'total_teaching_staff': total,
            'phd_completed': qs.filter(phd_status='completed').count(),
            'phd_pursuing': qs.filter(phd_status='pursuing').count(),
            'net_set_qualified': qs.filter(net_set_qualified=True).count(),
            'phd_percentage': round(
                qs.filter(phd_status='completed').count() / max(total, 1) * 100, 2
            ),
            'net_set_percentage': round(
                qs.filter(net_set_qualified=True).count() / max(total, 1) * 100, 2
            ),
            'avg_experience': qs.aggregate(
                avg=Avg('total_experience_years')
            )['avg'] or 0,
        }
        return Response(data)

    @action(detail=False, methods=['get'], url_path='export')
    def export(self, request):
        # Placeholder — Celery task se export hoga production mein
        return Response(
            {'message': 'Export task queued. File will be emailed.'},
            status=status.HTTP_202_ACCEPTED
        )
