from django.conf import settings
from rest_framework.pagination import PageNumberPagination


class CustomPagination(PageNumberPagination):
    """Кастомный пагинатор  с настройкой количества элементов на странице"""

    page_size_query_param = 'limit'
    page_size = getattr(settings, 'DEFAULT_PAGE_SIZE', 6)
