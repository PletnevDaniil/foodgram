from admin_auto_filters.filters import AutocompleteFilter
from django.contrib.admin import ModelAdmin, register
from django.contrib.auth.admin import UserAdmin
from django.db.models import Count

from .models import (
    Favorite, Follow, Ingredient,
    IngredientInRecipe, Recipe,
    ShoppingCart, Tag, User
)


class AuthorFilter(AutocompleteFilter):
    title = 'Автор'
    field_name = 'author'


class TagsFilter(AutocompleteFilter):
    title = 'Тег'
    field_name = 'tags'


class UserFilter(AutocompleteFilter):
    title = 'Пользователь'
    field_name = 'user'


class RecipeFilter(AutocompleteFilter):
    title = 'Рецепт'
    field_name = 'recipe'


class IngredientFilter(AutocompleteFilter):
    title = 'Ингредиент'
    field_name = 'ingredient'


@register(Ingredient)
class IngredientAdmin(ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)
    ordering = ('name',)


@register(Recipe)
class RecipeAdmin(ModelAdmin):
    list_display = (
        'name', 'author', 'get_favorites_count', 'get_tags', 'created'
    )
    list_filter = (AuthorFilter, TagsFilter)
    search_fields = ('name', 'author__username', 'tags__name')
    ordering = ('-created',)

    def get_queryset(self, request):
        """Оптимизация: аннотация + prefetch."""
        return super().get_queryset(request).prefetch_related(
            'tags',
            'author'
        ).annotate(
            favorites_count=Count('in_favorites')
        )

    def get_favorites_count(self, obj):
        return obj.favorites_count

    get_favorites_count.short_description = 'Добавлено в избранное (раз)'
    get_favorites_count.admin_order_field = 'favorites_count'

    def get_tags(self, obj):
        return ', '.join(obj.tags.values_list('name', flat=True))

    get_tags.short_description = 'Теги'


@register(User)
class MyUserAdmin(UserAdmin):
    list_display = (
        'username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff'
    )
    list_filter = ('is_active', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)


@register(Tag)
class TagAdmin(ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)
    ordering = ('name',)


@register(IngredientInRecipe)
class IngredientInRecipeAdmin(ModelAdmin):
    list_display = ('recipe', 'ingredient', 'amount')
    list_filter = (RecipeFilter, IngredientFilter)
    ordering = ('recipe',)


@register(ShoppingCart)
class ShoppingCartAdmin(ModelAdmin):
    list_display = ('user', 'recipe')
    list_filter = (UserFilter, RecipeFilter)
    search_fields = ('user__username', 'recipe__name')
    ordering = ('user',)


@register(Follow)
class FollowAdmin(ModelAdmin):
    list_display = ('user', 'author')
    list_filter = (UserFilter, 'author')
    search_fields = ('user__username', 'author__username')
    ordering = ('user',)


@register(Favorite)
class FavoriteAdmin(ModelAdmin):
    list_display = ('user', 'recipe')
    list_filter = (UserFilter, RecipeFilter)
    search_fields = ('user__username', 'recipe__name')
    ordering = ('user',)
