from rest_framework.pagination import PageNumberPagination
from django.conf import settings


class CustomPagination(PageNumberPagination):
    """Пагинатор с поддержкой ?limit=N (макс. 100)."""

    page_size_query_param = 'limit'
    max_page_size = settings.PAGINATION_MAX_PAGE_SIZE
    page_size = settings.PAGINATION_PAGE_SIZE
