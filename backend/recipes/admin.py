from django.contrib.admin import ModelAdmin, register
from django.contrib.auth.admin import UserAdmin

from .models import (
    Favorite, Follow, Ingredient,
    IngredientInRecipe, Recipe,
    ShoppingCart, Tag, User
)


@register(Ingredient)
class IngredientAdmin(ModelAdmin):
    list_display = ('pk', 'name', 'measurement_unit')
    search_fields = ('name',)


@register(Recipe)
class RecipeAdmin(ModelAdmin):
    list_display = (
        'pk', 'name', 'author', 'get_favorites', 'get_tags', 'created'
    )
    list_filter = ('author', 'name', 'tags')
    search_fields = ('name',)

    def get_queryset(self, request):
        """Оптимизация запроса: prefetch tags и in_favorites."""
        return super().get_queryset(request).prefetch_related(
            'tags',
            'in_favorites'
        )

    def get_favorites(self, obj):
        return obj.in_favorites.count()

    get_favorites.short_description = [
        'Количество добавлений рецепта в избранное'
    ]

    def get_tags(self, obj):
        return ', '.join(obj.tags.values_list('name', flat=True))

    get_tags.short_description = 'Теги'


@register(User)
class MyUserAdmin(UserAdmin):
    list_display = ('pk', 'username', 'email', 'first_name', 'last_name',
                    'password')
    list_filter = ('username', 'email')
    search_fields = ('username', 'email')


@register(Tag)
class TagAdmin(ModelAdmin):
    list_display = ('pk', 'name', 'slug')


@register(IngredientInRecipe)
class IngredientInRecipeAdmin(ModelAdmin):
    list_display = ('pk', 'recipe', 'ingredient', 'amount')


@register(ShoppingCart)
class ShoppingCartAdmin(ModelAdmin):
    list_display = ('pk', 'user', 'recipe')


@register(Follow)
class FollowAdmin(ModelAdmin):
    list_display = ('pk', 'user', 'author')
    search_fields = ('user', 'author')
    list_filter = ('user', 'author')


@register(Favorite)
class FavoriteAdmin(ModelAdmin):
    list_display = ('pk', 'user', 'recipe')
