from rest_framework.pagination import PageNumberPagination


class CustomPagination(PageNumberPagination):
    """Пагинатор с поддержкой ?limit=N (макс. 100)"""

    page_size_query_param = 'limit'
    max_page_size = 100
    page_size = 6
