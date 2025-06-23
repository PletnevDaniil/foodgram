from django_filters import rest_framework as filters
from django_filters.rest_framework import FilterSet

from recipes.models import Ingredient, Recipe, Tag


class IngredientFilter(FilterSet):
    """Фильтр для поиска ингредиентов по названию."""

    name = filters.CharFilter(
        field_name='name',
        lookup_expr='istartswith',
        help_text='Фильтрация по началу названия ингредиента'
    )

    class Meta:
        model = Ingredient
        fields = ('name', )


class RecipeFilter(FilterSet):
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

    def filter_favorited(self, queryset, name, value):
        """Фильтрация рецептов в избранном."""
        if value and self.request.user.is_authenticated:
            return queryset.filter(favorites__user=self.request.user)
        return queryset

    def filter_shopping_cart(self, queryset, name, value):
        """Фильтрация рецептов в списке покупок."""
        if value and self.request.user.is_authenticated:
            return queryset.filter(shopping_recipe__user=self.request.user)
        return queryset

    class Meta:
        model = Recipe
        fields = {
            'author': ['exact'],
            'tags': ['exact'],
        }
