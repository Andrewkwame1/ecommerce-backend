from rest_framework.pagination import PageNumberPagination


class StandardPagination(PageNumberPagination):
    """Standard pagination for list views"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class LargePagination(PageNumberPagination):
    """Large pagination for heavy queries"""
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 200
