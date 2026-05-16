from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class ProductList(APIView):
    def get(self, request):
        data = {
            "status": "success",
            "message": "API is working!",
            "products": [
                {"id": 1, "name": "Test Product", "price": 100}
            ]
        }
        return Response(data, status=status.HTTP_200_OK)
