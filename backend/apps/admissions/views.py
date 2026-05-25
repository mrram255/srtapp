from apps.core.responses import APIResponse
from apps.core.views import BaseAPIView

from .models import AdmissionApplication
from .serializers import AdmissionApplicationSerializer, AdmissionApplicationWriteSerializer


def _scope_admissions(queryset, user):
    if user.role == 'SUPER_ADMIN':
        return queryset
    if user.role == 'ADMIN' and getattr(user, 'college_id', None):
        return queryset.filter(college_id=user.college_id)
    return queryset.none()


class AdmissionListView(BaseAPIView):
    allowed_roles = ['SUPER_ADMIN', 'ADMIN']

    def get(self, request):
        queryset = AdmissionApplication.objects.filter(is_deleted=False).select_related(
            'department',
            'branch',
        )
        queryset = _scope_admissions(queryset, request.user)

        status_param = request.query_params.get('status')
        department_id = request.query_params.get('department')

        if status_param:
            queryset = queryset.filter(status=status_param.upper())
        if department_id:
            queryset = queryset.filter(department_id=department_id)

        return APIResponse.paginated(queryset, AdmissionApplicationSerializer, request)

    def post(self, request):
        serializer = AdmissionApplicationWriteSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return APIResponse.error(message='Invalid input.', errors=serializer.errors)

        app = serializer.save()
        return APIResponse.success(
            data=AdmissionApplicationSerializer(app).data,
            message='Application submitted.',
            status=201,
        )
