from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

# Custom pagination class
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response({
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'current_page': self.page.number,  
            'total_pages': self.page.paginator.num_pages,  
            'count': self.page.paginator.count,  
            'page_size': self.page_size,  
            'results': data  
        })
