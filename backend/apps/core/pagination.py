from django.utils import timezone
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class StandardPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'limit'
    max_page_size = 50

    def get_paginated_response(self, data):
        return Response(
            {
                "success": True,
                "message": "Success",
                "data": data,
                "meta": {
                    "total": self.page.paginator.count,
                    "page": self.page.number,
                    "limit": self.page_size,
                    "pages": self.page.paginator.num_pages,
                    "next": self.get_next_link(),
                    "previous": self.get_previous_link(),
                },
                "timestamp": timezone.now().isoformat(),
            }
        )
