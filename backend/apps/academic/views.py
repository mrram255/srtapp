from __future__ import annotations

import django_filters
from django.db.models import Count, Q
from rest_framework import filters, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.academic.models import (
    AcademicEvent,
    Batch,
    CurriculumSubject,
    HolidayCalendar,
    Program,
    Regulation,
    Section,
    Semester,
)
from apps.academic.serializers import (
    AcademicEventSerializer,
    AcademicYearListSerializer,
    AcademicYearWriteSerializer,
    BatchDetailSerializer,
    BatchListSerializer,
    DepartmentDetailSerializer,
    DepartmentListSerializer,
    DepartmentWriteSerializer,
    HolidaySerializer,
    ProgramDetailSerializer,
    ProgramListSerializer,
    ProgramWriteSerializer,
    RegulationDetailSerializer,
    RegulationListSerializer,
    SectionListSerializer,
    SectionWriteSerializer,
    SemesterSerializer,
    SubjectDetailSerializer,
    SubjectListSerializer,
    SubjectWriteSerializer,
)
from apps.colleges.models import AcademicYear, Department
from apps.core.permissions import IsSuperAdmin
from apps.core.responses import APIResponse


def _super_admin_write_permissions(view, action):
    if action in {'list', 'retrieve', 'programs', 'faculty', 'stats', 'subjects', 'batches', 'calendar'}:
        return [IsAuthenticated()]
    return [IsAuthenticated(), IsSuperAdmin()]


class AcademicYearViewSet(viewsets.ModelViewSet):
    queryset = AcademicYear.objects.filter(is_deleted=False).select_related('college')
    filterset_fields = ['college', 'is_current', 'is_active']
    search_fields = ['year']
    ordering_fields = ['year', 'start_date']
    ordering = ['-year']

    def get_permissions(self):
        return _super_admin_write_permissions(self, self.action)

    def get_serializer_class(self):
        if self.action in {'create', 'update', 'partial_update'}:
            return AcademicYearWriteSerializer
        return AcademicYearListSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        return APIResponse.paginated(queryset, AcademicYearListSerializer, request)

    def retrieve(self, request, *args, **kwargs):
        obj = self.get_object()
        return APIResponse.success(AcademicYearListSerializer(obj).data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return APIResponse.error(message='Validation Error', errors=serializer.errors, status=400)
        obj = serializer.save()
        return APIResponse.success(AcademicYearListSerializer(obj).data, message='Academic year created.', status=201)

    def update(self, request, *args, **kwargs):
        obj = self.get_object()
        serializer = self.get_serializer(obj, data=request.data, partial=kwargs.get('partial', False))
        if not serializer.is_valid():
            return APIResponse.error(message='Validation Error', errors=serializer.errors, status=400)
        obj = serializer.save()
        return APIResponse.success(AcademicYearListSerializer(obj).data, message='Academic year updated.')

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.is_active = False
        obj.save(update_fields=['is_active'])
        return APIResponse.success(message='Academic year deactivated.')

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        obj = self.get_object()
        AcademicYear.objects.filter(college=obj.college, is_current=True).exclude(pk=obj.pk).update(is_current=False)
        obj.is_current = True
        obj.save(update_fields=['is_current'])
        return APIResponse.success(AcademicYearListSerializer(obj).data, message='Academic year activated.')


class DepartmentFilter(django_filters.FilterSet):
    college = django_filters.UUIDFilter(field_name='college_id')
    search = django_filters.CharFilter(method='filter_search')

    class Meta:
        model = Department
        fields = ['college', 'is_active']

    def filter_search(self, queryset, name, value):
        return queryset.filter(Q(name__icontains=value) | Q(code__icontains=value))


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.filter(is_deleted=False).select_related('college', 'hod')
    filterset_class = DepartmentFilter
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = ['name', 'code']
    ordering = ['name']

    def get_permissions(self):
        return _super_admin_write_permissions(self, self.action)

    def get_queryset(self):
        qs = super().get_queryset()
        if self.action == 'list':
            return qs.annotate(program_count=Count('programs', filter=Q(programs__is_active=True)))
        return qs

    def get_serializer_class(self):
        if self.action == 'list':
            return DepartmentListSerializer
        if self.action in {'create', 'update', 'partial_update'}:
            return DepartmentWriteSerializer
        return DepartmentDetailSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        return APIResponse.paginated(queryset, DepartmentListSerializer, request)

    def retrieve(self, request, *args, **kwargs):
        return APIResponse.success(DepartmentDetailSerializer(self.get_object()).data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return APIResponse.error(message='Validation Error', errors=serializer.errors, status=400)
        dept = serializer.save()
        return APIResponse.success(DepartmentDetailSerializer(dept).data, message='Department created.', status=201)

    def update(self, request, *args, **kwargs):
        dept = self.get_object()
        serializer = self.get_serializer(dept, data=request.data, partial=kwargs.get('partial', False))
        if not serializer.is_valid():
            return APIResponse.error(message='Validation Error', errors=serializer.errors, status=400)
        dept = serializer.save()
        return APIResponse.success(DepartmentDetailSerializer(dept).data, message='Department updated.')

    def destroy(self, request, *args, **kwargs):
        dept = self.get_object()
        dept.is_active = False
        dept.save(update_fields=['is_active'])
        return APIResponse.success(message='Department deactivated.')

    @action(detail=True, methods=['get'])
    def programs(self, request, pk=None):
        dept = self.get_object()
        programs = Program.objects.filter(department=dept, is_active=True)
        return APIResponse.paginated(programs, ProgramListSerializer, request)

    @action(detail=True, methods=['get'])
    def faculty(self, request, pk=None):
        dept = self.get_object()
        from django.contrib.auth import get_user_model

        User = get_user_model()
        faculty = User.objects.filter(department=dept, is_deleted=False, is_active=True)
        data = [
            {
                'id': str(u.id),
                'full_name': u.get_full_name(),
                'email': u.email,
                'role': u.role,
            }
            for u in faculty[:50]
        ]
        return APIResponse.success(data)

    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        dept = self.get_object()
        return APIResponse.success(
            {
                'department_id': str(dept.id),
                'programs': Program.objects.filter(department=dept, is_active=True).count(),
                'batches': Batch.objects.filter(program__department=dept, is_active=True).count(),
                'subjects': CurriculumSubject.objects.filter(program__department=dept, is_active=True).count(),
            }
        )


class RegulationViewSet(viewsets.ModelViewSet):
    queryset = Regulation.objects.select_related('college', 'effective_from').all()
    filterset_fields = ['college', 'regulation_type', 'is_active']
    search_fields = ['name', 'code']
    ordering = ['name']

    def get_permissions(self):
        return _super_admin_write_permissions(self, self.action)

    def get_serializer_class(self):
        if self.action == 'list':
            return RegulationListSerializer
        if self.action in {'create', 'update', 'partial_update'}:
            return RegulationDetailSerializer
        return RegulationDetailSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        return APIResponse.paginated(queryset, RegulationListSerializer, request)

    def retrieve(self, request, *args, **kwargs):
        return APIResponse.success(RegulationDetailSerializer(self.get_object()).data)

    def create(self, request, *args, **kwargs):
        serializer = RegulationDetailSerializer(data=request.data)
        if not serializer.is_valid():
            return APIResponse.error(message='Validation Error', errors=serializer.errors, status=400)
        obj = serializer.save(created_by=request.user, updated_by=request.user)
        return APIResponse.success(RegulationDetailSerializer(obj).data, message='Regulation created.', status=201)

    def update(self, request, *args, **kwargs):
        obj = self.get_object()
        serializer = RegulationDetailSerializer(obj, data=request.data, partial=kwargs.get('partial', False))
        if not serializer.is_valid():
            return APIResponse.error(message='Validation Error', errors=serializer.errors, status=400)
        obj = serializer.save(updated_by=request.user)
        return APIResponse.success(RegulationDetailSerializer(obj).data, message='Regulation updated.')

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.is_active = False
        obj.save(update_fields=['is_active'])
        return APIResponse.success(message='Regulation deactivated.')


class ProgramViewSet(viewsets.ModelViewSet):
    queryset = Program.objects.select_related('department', 'college', 'regulation').all()
    filterset_fields = ['college', 'department', 'level', 'is_active']
    search_fields = ['name', 'code']
    ordering_fields = ['order', 'name']
    ordering = ['order', 'name']

    def get_permissions(self):
        return _super_admin_write_permissions(self, self.action)

    def get_queryset(self):
        qs = super().get_queryset()
        if self.action == 'list':
            return qs.annotate(
                subject_count=Count('subjects', filter=Q(subjects__is_active=True)),
                batch_count=Count('batches', filter=Q(batches__is_active=True)),
            )
        return qs

    def get_serializer_class(self):
        if self.action == 'list':
            return ProgramListSerializer
        if self.action in {'create', 'update', 'partial_update'}:
            return ProgramWriteSerializer
        return ProgramDetailSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        return APIResponse.paginated(queryset, ProgramListSerializer, request)

    def retrieve(self, request, *args, **kwargs):
        return APIResponse.success(ProgramDetailSerializer(self.get_object()).data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return APIResponse.error(message='Validation Error', errors=serializer.errors, status=400)
        obj = serializer.save(created_by=request.user, updated_by=request.user)
        return APIResponse.success(ProgramDetailSerializer(obj).data, message='Program created.', status=201)

    def update(self, request, *args, **kwargs):
        obj = self.get_object()
        serializer = self.get_serializer(obj, data=request.data, partial=kwargs.get('partial', False))
        if not serializer.is_valid():
            return APIResponse.error(message='Validation Error', errors=serializer.errors, status=400)
        obj = serializer.save(updated_by=request.user)
        return APIResponse.success(ProgramDetailSerializer(obj).data, message='Program updated.')

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.is_active = False
        obj.save(update_fields=['is_active'])
        return APIResponse.success(message='Program deactivated.')

    @action(detail=True, methods=['get'])
    def subjects(self, request, pk=None):
        program = self.get_object()
        subjects = CurriculumSubject.objects.filter(program=program, is_active=True)
        semester = request.query_params.get('semester')
        if semester:
            subjects = subjects.filter(semester_number=semester)
        return APIResponse.paginated(subjects, SubjectListSerializer, request)

    @action(detail=True, methods=['get'])
    def batches(self, request, pk=None):
        program = self.get_object()
        batches = Batch.objects.filter(program=program, is_active=True)
        return APIResponse.paginated(batches, BatchListSerializer, request)


class BatchViewSet(viewsets.ModelViewSet):
    queryset = Batch.objects.select_related('program', 'academic_year').all()
    filterset_fields = ['program', 'academic_year', 'is_active']
    search_fields = ['name']
    ordering = ['-start_year']

    def get_permissions(self):
        return _super_admin_write_permissions(self, self.action)

    def get_queryset(self):
        qs = super().get_queryset()
        if self.action == 'list':
            return qs.annotate(section_count=Count('sections', filter=Q(sections__is_active=True)))
        return qs

    def get_serializer_class(self):
        if self.action == 'list':
            return BatchListSerializer
        if self.action in {'create', 'update', 'partial_update'}:
            return BatchDetailSerializer
        return BatchDetailSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        return APIResponse.paginated(queryset, BatchListSerializer, request)

    def retrieve(self, request, *args, **kwargs):
        return APIResponse.success(BatchDetailSerializer(self.get_object()).data)

    def create(self, request, *args, **kwargs):
        serializer = BatchDetailSerializer(data=request.data)
        if not serializer.is_valid():
            return APIResponse.error(message='Validation Error', errors=serializer.errors, status=400)
        obj = serializer.save(created_by=request.user, updated_by=request.user)
        return APIResponse.success(BatchDetailSerializer(obj).data, message='Batch created.', status=201)

    def update(self, request, *args, **kwargs):
        obj = self.get_object()
        serializer = BatchDetailSerializer(obj, data=request.data, partial=kwargs.get('partial', False))
        if not serializer.is_valid():
            return APIResponse.error(message='Validation Error', errors=serializer.errors, status=400)
        obj = serializer.save(updated_by=request.user)
        return APIResponse.success(BatchDetailSerializer(obj).data, message='Batch updated.')

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.is_active = False
        obj.save(update_fields=['is_active'])
        return APIResponse.success(message='Batch deactivated.')


class SectionViewSet(viewsets.ModelViewSet):
    queryset = Section.objects.select_related('batch', 'class_teacher').all()
    filterset_fields = ['batch', 'is_active']
    search_fields = ['name']
    ordering = ['name']

    def get_permissions(self):
        return _super_admin_write_permissions(self, self.action)

    def get_serializer_class(self):
        if self.action in {'create', 'update', 'partial_update'}:
            return SectionWriteSerializer
        return SectionListSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        return APIResponse.paginated(queryset, SectionListSerializer, request)

    def retrieve(self, request, *args, **kwargs):
        return APIResponse.success(SectionListSerializer(self.get_object()).data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return APIResponse.error(message='Validation Error', errors=serializer.errors, status=400)
        obj = serializer.save(created_by=request.user, updated_by=request.user)
        return APIResponse.success(SectionListSerializer(obj).data, message='Section created.', status=201)

    def update(self, request, *args, **kwargs):
        obj = self.get_object()
        serializer = self.get_serializer(obj, data=request.data, partial=kwargs.get('partial', False))
        if not serializer.is_valid():
            return APIResponse.error(message='Validation Error', errors=serializer.errors, status=400)
        obj = serializer.save(updated_by=request.user)
        return APIResponse.success(SectionListSerializer(obj).data, message='Section updated.')

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.is_active = False
        obj.save(update_fields=['is_active'])
        return APIResponse.success(message='Section deactivated.')


class SemesterViewSet(viewsets.ModelViewSet):
    queryset = Semester.objects.select_related('academic_year', 'batch').all()
    filterset_fields = ['academic_year', 'batch', 'is_current', 'status']
    ordering = ['semester_number']

    def get_permissions(self):
        return _super_admin_write_permissions(self, self.action)

    serializer_class = SemesterSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        return APIResponse.paginated(queryset, SemesterSerializer, request)

    def retrieve(self, request, *args, **kwargs):
        return APIResponse.success(SemesterSerializer(self.get_object()).data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return APIResponse.error(message='Validation Error', errors=serializer.errors, status=400)
        obj = serializer.save(created_by=request.user, updated_by=request.user)
        return APIResponse.success(SemesterSerializer(obj).data, message='Semester created.', status=201)

    def update(self, request, *args, **kwargs):
        obj = self.get_object()
        serializer = self.get_serializer(obj, data=request.data, partial=kwargs.get('partial', False))
        if not serializer.is_valid():
            return APIResponse.error(message='Validation Error', errors=serializer.errors, status=400)
        obj = serializer.save(updated_by=request.user)
        return APIResponse.success(SemesterSerializer(obj).data, message='Semester updated.')

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.is_active = False
        obj.save(update_fields=['is_active'])
        return APIResponse.success(message='Semester deactivated.')


class SubjectViewSet(viewsets.ModelViewSet):
    queryset = CurriculumSubject.objects.select_related('program', 'college', 'regulation').all()
    filterset_fields = ['college', 'program', 'semester_number', 'subject_type', 'category', 'is_active']
    search_fields = ['name', 'code']
    ordering = ['semester_number', 'name']

    def get_permissions(self):
        return _super_admin_write_permissions(self, self.action)

    def get_serializer_class(self):
        if self.action == 'list':
            return SubjectListSerializer
        if self.action in {'create', 'update', 'partial_update'}:
            return SubjectWriteSerializer
        return SubjectDetailSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        return APIResponse.paginated(queryset, SubjectListSerializer, request)

    def retrieve(self, request, *args, **kwargs):
        return APIResponse.success(SubjectDetailSerializer(self.get_object()).data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return APIResponse.error(message='Validation Error', errors=serializer.errors, status=400)
        obj = serializer.save(created_by=request.user, updated_by=request.user)
        return APIResponse.success(SubjectDetailSerializer(obj).data, message='Subject created.', status=201)

    def update(self, request, *args, **kwargs):
        obj = self.get_object()
        serializer = self.get_serializer(obj, data=request.data, partial=kwargs.get('partial', False))
        if not serializer.is_valid():
            return APIResponse.error(message='Validation Error', errors=serializer.errors, status=400)
        obj = serializer.save(updated_by=request.user)
        return APIResponse.success(SubjectDetailSerializer(obj).data, message='Subject updated.')

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.is_active = False
        obj.save(update_fields=['is_active'])
        return APIResponse.success(message='Subject deactivated.')


class HolidayViewSet(viewsets.ModelViewSet):
    queryset = HolidayCalendar.objects.prefetch_related('departments').select_related('academic_year').all()
    filterset_fields = ['academic_year', 'holiday_type', 'date']
    search_fields = ['name']
    ordering = ['date']

    def get_permissions(self):
        return _super_admin_write_permissions(self, self.action)

    serializer_class = HolidaySerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        return APIResponse.paginated(queryset, HolidaySerializer, request)

    def retrieve(self, request, *args, **kwargs):
        return APIResponse.success(HolidaySerializer(self.get_object()).data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return APIResponse.error(message='Validation Error', errors=serializer.errors, status=400)
        obj = serializer.save(created_by=request.user, updated_by=request.user)
        return APIResponse.success(HolidaySerializer(obj).data, message='Holiday created.', status=201)

    def update(self, request, *args, **kwargs):
        obj = self.get_object()
        serializer = self.get_serializer(obj, data=request.data, partial=kwargs.get('partial', False))
        if not serializer.is_valid():
            return APIResponse.error(message='Validation Error', errors=serializer.errors, status=400)
        obj = serializer.save(updated_by=request.user)
        return APIResponse.success(HolidaySerializer(obj).data, message='Holiday updated.')

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.is_active = False
        obj.save(update_fields=['is_active'])
        return APIResponse.success(message='Holiday removed.')


class AcademicEventViewSet(viewsets.ModelViewSet):
    queryset = AcademicEvent.objects.prefetch_related('applicable_departments').select_related('academic_year').all()
    filterset_fields = ['academic_year', 'event_type']
    search_fields = ['title']
    ordering = ['start_date']

    def get_permissions(self):
        return _super_admin_write_permissions(self, self.action)

    serializer_class = AcademicEventSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        return APIResponse.paginated(queryset, AcademicEventSerializer, request)

    def retrieve(self, request, *args, **kwargs):
        return APIResponse.success(AcademicEventSerializer(self.get_object()).data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return APIResponse.error(message='Validation Error', errors=serializer.errors, status=400)
        obj = serializer.save(created_by=request.user, updated_by=request.user)
        return APIResponse.success(AcademicEventSerializer(obj).data, message='Event created.', status=201)

    def update(self, request, *args, **kwargs):
        obj = self.get_object()
        serializer = self.get_serializer(obj, data=request.data, partial=kwargs.get('partial', False))
        if not serializer.is_valid():
            return APIResponse.error(message='Validation Error', errors=serializer.errors, status=400)
        obj = serializer.save(updated_by=request.user)
        return APIResponse.success(AcademicEventSerializer(obj).data, message='Event updated.')

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.is_active = False
        obj.save(update_fields=['is_active'])
        return APIResponse.success(message='Event removed.')


class AcademicCalendarView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        academic_year_id = request.query_params.get('academic_year')
        holidays = HolidayCalendar.objects.filter(is_active=True)
        events = AcademicEvent.objects.filter(is_active=True)
        if academic_year_id:
            holidays = holidays.filter(academic_year_id=academic_year_id)
            events = events.filter(academic_year_id=academic_year_id)
        return APIResponse.success(
            {
                'holidays': HolidaySerializer(holidays.order_by('date')[:200], many=True).data,
                'events': AcademicEventSerializer(events.order_by('start_date')[:200], many=True).data,
            }
        )
