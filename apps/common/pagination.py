from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
import math

class CustomPageNumberPagination(PageNumberPagination):
    """
    Custom pagination to match the Regular boilerplate response format.
    Query params: ?page=1&limit=10
    """
    page_size_query_param = 'limit'  # Allow client to set limit via ?limit=
    max_page_size = 100
    
    def get_paginated_response(self, data):
        # Calculate total pages
        total_results = self.page.paginator.count
        limit = self.get_page_size(self.request)
        total_pages = math.ceil(total_results / limit) if limit else 1
        current_page = self.page.number

        return Response({
            'results': data,
            'page': current_page,
            'limit': limit,
            'totalPages': total_pages,
            'totalResults': total_results
        })