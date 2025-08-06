from django.db.models import Prefetch, Sum, Count
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import response, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import (
    AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
)
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from recipes.models import (
    Favorite, Follow, Ingredient, IngredientInRecipe,
    Recipe, ShoppingCart, Tag, User
)
from .filters import IngredientFilter, RecipeFilter
from .pagination import CustomPagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (AddFavoritesSerializer, CreateRecipeSerializer,
                          FollowRepresentationSerializer,
                          FollowCreateSerializer,
                          IngredientSerializer,
                          RecipeSerializer, TagSerializer,
                          ToggleRelationSerializer,
                          UserAvatarSerializer, UserSerializer)
from .utils import generate_shopping_list_pdf


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для работы с тегами."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для работы с ингредиентами."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    search_fields = ('^name',)


class UserViewSet(UserViewSet):
    """Вьюсет для работы с пользователями и подписками."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = LimitOffsetPagination

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(IsAuthenticated, ),
        url_path='subscriptions',
        url_name='subscriptions',
    )
    def subscriptions(self, request):
        queryset = User.objects.filter(
            followers__user=request.user
        ).annotate(
            recipes_count=Count('recipes')
        ).prefetch_related(
            Prefetch(
                'recipes',
                queryset=Recipe.objects.all()
            )
        ).distinct()
        pages = self.paginate_queryset(queryset)
        serializer = FollowRepresentationSerializer(
            pages, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(IsAuthenticated,),
        url_path='subscribe',
        url_name='subscribe',
    )
    def subscribe(self, request, id):
        user = request.user
        author = get_object_or_404(User, id=id)

        serializer = FollowCreateSerializer(
            instance=author,
            data={},
            context={'request': request}
        )

        if request.method == 'POST':
            serializer = FollowCreateSerializer(
                data={},
                context={'request': request, 'author': author}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            representation = FollowRepresentationSerializer(
                author,
                context={'request': request}
            )
            return Response(
                representation.data,
                status=status.HTTP_201_CREATED
            )

        if request.method == 'DELETE':
            deleted_count, _ = Follow.objects.filter(
                user=user,
                author=author
            ).delete()
            if deleted_count == 0:
                return Response(
                    {'errors': 'Вы не подписаны на этого пользователя'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        ['PUT'],
        detail=False,
        url_path='me/avatar',
        name='set_avatar',
        permission_classes=[IsAuthenticated]
    )
    def avatar(self, request: Request, *args, **kwargs):
        if 'avatar' not in request.data:
            return response.Response(
                {'avatar': 'Отсутствует изображение'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = UserAvatarSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        avatar_data = serializer.validated_data.get('avatar')
        request.user.avatar = avatar_data
        request.user.save()

        image_url = request.build_absolute_uri(
            f'/media/users/{avatar_data.name}'
        )
        return response.Response(
            {'avatar': str(image_url)}, status=status.HTTP_200_OK
        )

    @avatar.mapping.delete
    def delete_avatar(self, request: Request, *args, **kwargs):
        user = self.request.user
        if user.avatar:
            user.avatar.delete()
        return response.Response(status=status.HTTP_204_NO_CONTENT)


class RecipeViewSet(ModelViewSet):
    """Вьюсет для работы с рецептами."""

    queryset = Recipe.objects.all()
    pagination_class = CustomPagination
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от действия."""
        if self.action in ('list', 'retrieve'):
            return RecipeSerializer
        elif self.action in ('create', 'partial_update'):
            return CreateRecipeSerializer

    def get_serializer_context(self):
        """Добавление request в контекст сериализатора."""
        context = super().get_serializer_context()
        context.update({'request': self.request})
        return context

    def _toggle_relation(self, request, pk, model_class, related_name):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)

        context = {
            'request': request,
            'model_class': model_class,
            'related_name': related_name
        }

        if request.method == 'POST':
            serializer = ToggleRelationSerializer(
                data={'recipe_id': pk},
                context=context
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            response_serializer = AddFavoritesSerializer(recipe)
            return Response(
                response_serializer.data,
                status=status.HTTP_201_CREATED
            )

        elif request.method == 'DELETE':
            deleted_count, _ = model_class.objects.filter(
                user=user, recipe=recipe
            ).delete()
            if deleted_count == 0:
                return Response(
                    {'errors': f'Рецепт "{recipe.name}" не в {related_name}.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(IsAuthenticated,),
        url_path='favorite',
        url_name='favorite',
    )
    def favorite(self, request, pk):
        return self._toggle_relation(request, pk, Favorite, 'избранном')

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(IsAuthenticated,),
        url_path='shopping_cart',
        url_name='shopping_cart',
    )
    def shopping_cart(self, request, pk):
        return self._toggle_relation(
            request, pk, ShoppingCart, 'списке покупок'
        )

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(IsAuthenticated,),
        url_path='download_shopping_cart',
        url_name='download_shopping_cart',
    )
    def download_shopping_cart(self, request):
        """Метод для загрузки списка покупок в pdf формате."""
        ingredients = IngredientInRecipe.objects.filter(
            recipe__in_shopping_carts__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(sum=Sum('amount'))

        pdf_shopping_list = generate_shopping_list_pdf(ingredients)
        response = FileResponse(
            pdf_shopping_list,
            content_type='application/pdf'
        )
        response['Content-Disposition'] = (
            'attachment; filename="shopping_list.pdf"'
        )
        return response
