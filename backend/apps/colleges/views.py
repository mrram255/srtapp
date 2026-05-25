from apps.core.responses import APIResponse
from apps.core.views import BaseAPIView

from .models import AcademicYear, Branch, College, Department
from .serializers import (
    AcademicYearSerializer,
    BranchSerializer,
    CollegeSerializer,
    DepartmentSerializer,
)


class CollegeListView(BaseAPIView):
    allowed_roles = ['SUPER_ADMIN']

    def get(self, request):
        queryset = College.objects.filter(is_deleted=False)
        return APIResponse.paginated(queryset, CollegeSerializer, request)

    def post(self, request):
        serializer = CollegeSerializer(data=request.data)
        if serializer.is_valid():
            college = serializer.save()
            return APIResponse.success(
                data=CollegeSerializer(college).data,
                message='College created successfully.',
                status=201,
            )
        return APIResponse.error(message='Invalid input.', errors=serializer.errors)


class CollegeDetailView(BaseAPIView):
    allowed_roles = ['SUPER_ADMIN', 'ADMIN']

    def get(self, request, pk):
        try:
            college = College.objects.get(id=pk, is_deleted=False)
            if request.user.role == 'ADMIN' and college != request.user.college:
                return APIResponse.error(message='Access denied.', status=403)
            serializer = CollegeSerializer(college)
            return APIResponse.success(data=serializer.data)
        except College.DoesNotExist:
            return APIResponse.error(message='College not found.', status=404)

    def patch(self, request, pk):
        try:
            college = College.objects.get(id=pk, is_deleted=False)
            if request.user.role == 'ADMIN' and college != request.user.college:
                return APIResponse.error(message='Access denied.', status=403)

            serializer = CollegeSerializer(college, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return APIResponse.success(data=serializer.data, message='College updated successfully.')
            return APIResponse.error(message='Invalid input.', errors=serializer.errors)
        except College.DoesNotExist:
            return APIResponse.error(message='College not found.', status=404)


class DepartmentListView(BaseAPIView):
    allowed_roles = ['SUPER_ADMIN', 'ADMIN', 'HOD']

    def get(self, request):
        queryset = Department.objects.filter(is_deleted=False, is_active=True)
        queryset = self.scope_to_role(queryset, request.user)

        college_id = request.query_params.get('college')
        if college_id:
            queryset = queryset.filter(college_id=college_id)

        return APIResponse.paginated(queryset, DepartmentSerializer, request)

    def post(self, request):
        serializer = DepartmentSerializer(data=request.data)
        if serializer.is_valid():
            if request.user.role != 'SUPER_ADMIN':
                serializer.validated_data['college'] = request.user.college
            dept = serializer.save()
            return APIResponse.success(
                data=DepartmentSerializer(dept).data,
                message='Department created successfully.',
                status=201,
            )
        return APIResponse.error(message='Invalid input.', errors=serializer.errors)


class DepartmentDetailView(BaseAPIView):
    allowed_roles = ['SUPER_ADMIN', 'ADMIN', 'HOD']

    def get(self, request, pk):
        try:
            dept = Department.objects.get(id=pk, is_deleted=False)
            if request.user.role != 'SUPER_ADMIN' and dept.college != request.user.college:
                return APIResponse.error(message='Access denied.', status=403)
            serializer = DepartmentSerializer(dept)
            return APIResponse.success(data=serializer.data)
        except Department.DoesNotExist:
            return APIResponse.error(message='Department not found.', status=404)


class BranchListView(BaseAPIView):
    allowed_roles = ['SUPER_ADMIN', 'ADMIN', 'HOD', 'TEACHER']

    def get(self, request):
        queryset = Branch.objects.filter(is_deleted=False, is_active=True)
        queryset = self.scope_to_role(queryset, request.user)

        department_id = request.query_params.get('department')
        if department_id:
            queryset = queryset.filter(department_id=department_id)

        return APIResponse.paginated(queryset, BranchSerializer, request)


class AcademicYearListView(BaseAPIView):
    allowed_roles = ['SUPER_ADMIN', 'ADMIN', 'HOD', 'TEACHER', 'STUDENT']

    def get(self, request):
        queryset = AcademicYear.objects.filter(is_deleted=False)
        queryset = self.scope_to_role(queryset, request.user)

        is_current = request.query_params.get('is_current')
        if is_current is not None:
            queryset = queryset.filter(is_current=is_current.lower() == 'true')

        return APIResponse.paginated(queryset, AcademicYearSerializer, request)

    def post(self, request):
        serializer = AcademicYearSerializer(data=request.data)
        if serializer.is_valid():
            if request.user.role != 'SUPER_ADMIN':
                serializer.validated_data['college'] = request.user.college
            year = serializer.save()
            return APIResponse.success(
                data=AcademicYearSerializer(year).data,
                message='Academic year created successfully.',
                status=201,
            )
        return APIResponse.error(message='Invalid input.', errors=serializer.errors)
