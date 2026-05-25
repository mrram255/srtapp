from apps.colleges.models import College

from apps.core.responses import APIResponse
from apps.core.views import BaseAPIView

from .models import GateLog
from .serializers import GateLogSerializer, GateLogWriteSerializer


def _scope_gate_logs(queryset, user):
    if user.role == 'SUPER_ADMIN':
        return queryset
    if getattr(user, 'college_id', None):
        return queryset.filter(college_id=user.college_id)
    return queryset.none()


class GateLogListView(BaseAPIView):
    allowed_roles = ['SUPER_ADMIN', 'ADMIN', 'SECURITY']

    def get(self, request):
        queryset = GateLog.objects.filter(is_deleted=False).select_related(
            'person',
            'student',
            'meeting_with',
            'security_guard',
        )
        queryset = _scope_gate_logs(queryset, request.user)

        entry_type = request.query_params.get('entry_type')
        person_type = request.query_params.get('person_type')
        date_param = request.query_params.get('date')
        gate_number = request.query_params.get('gate_number')

        if entry_type:
            queryset = queryset.filter(entry_type=entry_type.upper())
        if person_type:
            queryset = queryset.filter(person_type=person_type.upper())
        if date_param:
            queryset = queryset.filter(timestamp__date=date_param)
        if gate_number:
            queryset = queryset.filter(gate_number__iexact=gate_number)

        return APIResponse.paginated(queryset, GateLogSerializer, request)

    def post(self, request):
        college = request.user.college
        if request.user.role == 'SUPER_ADMIN':
            cid = request.data.get('college')
            if not cid:
                return APIResponse.error(message='college is required.', status=400)
            college = College.objects.filter(pk=cid, is_deleted=False).first()
            if not college:
                return APIResponse.error(message='Invalid college.', status=400)

        if college is None:
            return APIResponse.error(message='College context required.', status=400)

        serializer = GateLogWriteSerializer(data=request.data, context={'request': request, 'college': college})
        if not serializer.is_valid():
            return APIResponse.error(message='Invalid input.', errors=serializer.errors)

        log = serializer.save()
        return APIResponse.success(data=GateLogSerializer(log).data, message='Gate log entry created.', status=201)
