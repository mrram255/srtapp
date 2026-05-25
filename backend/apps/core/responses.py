from django.utils import timezone
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class APIResponse:
    @staticmethod
    def success(data=None, message="Success", status=200, meta=None):
        return Response(
            {
                "success": True,
                "message": message,
                "data": data,
                "meta": meta,
                "timestamp": timezone.now().isoformat(),
            },
            status=status,
        )

    @staticmethod
    def error(message="An error occurred", errors=None, status=400):
        return Response(
            {
                "success": False,
                "message": message,
                "errors": errors,
                "timestamp": timezone.now().isoformat(),
            },
            status=status,
        )

    @staticmethod
    def paginated(queryset, serializer_class, request, page_size=20):
        paginator = PageNumberPagination()
        paginator.page_size = min(int(request.query_params.get('limit', page_size)), 50)
        page = paginator.paginate_queryset(queryset, request)
        data = serializer_class(page, many=True, context={'request': request}).data
        return APIResponse.success(
            data=data,
            meta={
                "total": paginator.page.paginator.count,
                "page": paginator.page.number,
                "limit": paginator.page_size,
                "pages": paginator.page.paginator.num_pages,
                "next": paginator.get_next_link(),
                "previous": paginator.get_previous_link(),
            },
        )
