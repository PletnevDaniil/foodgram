from django_filters import rest_framework as filters
from recipes.models import Ingredient, Recipe, Tag


class IngredientFilter(filters.FilterSet):
    """Фильтр для поиска ингредиентов по названию."""

    name = filters.CharFilter(
        field_name='name',
        lookup_expr='icontains',
        label='Поиск по названию (вхождение)',
        help_text='Ищет по вхождению текста в название'
    )

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(filters.FilterSet):
    """Фильтр для рецептов с поддержкой тегов, избранного и списка покупок."""

    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
        label='Фильтр по тегам (slug)',
        help_text='Можно выбрать несколько тегов'
    )

    is_favorited = filters.BooleanFilter(
        method='filter_favorited',
        label='В избранном',
        help_text='Показать только рецепты в избранном'
    )

    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_shopping_cart',
        label='В списке покупок',
        help_text='Показать только рецепты в списке покупок'
    )

    class Meta:
        model = Recipe
        fields = ('author', 'tags')

    def filter_favorited(self, queryset, name, value):
        """Фильтрация рецептов в избранном."""
        if value and self.request.user.is_authenticated:
            return queryset.filter(
                favorites__user=self.request.user
            ).distinct()
        return queryset.distinct()

    def filter_shopping_cart(self, queryset, name, value):
        """Фильтрация рецептов в списке покупок."""
        if value and self.request.user.is_authenticated:
            return queryset.filter(
                shopping_recipe__user=self.request.user
            ).distinct()
        return queryset.distinct()
