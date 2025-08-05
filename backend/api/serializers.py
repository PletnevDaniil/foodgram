from djoser.serializers import UserCreateSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from recipes.models import (
    Favorite,
    Follow,
    Ingredient,
    IngredientInRecipe,
    Recipe,
    ShoppingCart,
    Tag,
    User,
)


class TagSerializer(ModelSerializer):
    """Сериализатор для работы с тегами."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerializer(ModelSerializer):
    """Сериализатор для работы с ингредиентами."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class UserSerializer(UserCreateSerializer):
    """Сериализатор для работы с пользователями."""

    is_subscribed = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed', 'avatar'
        )

    def get_is_subscribed(self, obj):
        """Проверяет, подписан ли текущий пользователь на автора."""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return Follow.objects.filter(user=request.user, author=obj).exists()

    def get_avatar(self, obj):
        """Возвращает URL аватара или None, если аватар отсутствует."""
        return obj.avatar.url if obj.avatar else None


class UserAvatarSerializer(serializers.ModelSerializer):
    """Сериалайзер для работы с аватаром."""

    avatar = Base64ImageField(required=True)

    class Meta:
        model = User
        fields = ('avatar',)
        read_only_fields = ('id',)


class CreateUserSerializer(UserSerializer):
    """Сериализатор для создания пользователя
    без проверки на подписку."""

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'password'
        )
        extra_kwargs = {'password': {'write_only': True}}


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения ингредиентов в рецепте."""

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeShortSerializer(serializers.ModelSerializer):
    """Короткий сериализатор для рецептов (в избранном, подписках и т.д.)."""

    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для рецептов."""

    tags = TagSerializer(many=True)
    author = UserSerializer(read_only=True)
    ingredients = IngredientInRecipeSerializer(
        source='ingredient_list',
        many=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'is_favorited', 'is_in_shopping_cart',
            'name', 'image', 'text', 'cooking_time'
        )

    def get_is_favorited(self, obj):
        """Проверяет, добавлен ли рецепт в избранное."""
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Favorite.objects.filter(
            user=request.user, recipe=obj
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        """Проверяет, добавлен ли рецепт в список покупок."""
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            user=request.user, recipe=obj
        ).exists()


class CreateIngredientsInRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов в рецептах."""

    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    @staticmethod
    def validate_amount(value):
        """Метод валидации количества"""
        if value < 1:
            raise serializers.ValidationError(
                'Количество ингредиента должно быть больше 0!'
            )
        return value

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'amount')


class CreateRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для создания рецептов."""

    ingredients = CreateIngredientsInRecipeSerializer(
        many=True,
        allow_empty=False,
        required=True
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
        allow_empty=False,
        required=True
    )
    image = Base64ImageField(
        required=True,
        allow_null=False,
        use_url=True
    )

    class Meta:
        model = Recipe
        fields = ('ingredients', 'tags', 'name',
                  'image', 'text', 'cooking_time')

    def to_representation(self, instance):
        """Метод представления модели."""
        serializer = RecipeSerializer(
            instance,
            context={
                'request': self.context.get('request')
            }
        )
        return serializer.data

    def validate(self, data):
        """Основная валидация данных."""
        ingredients = self.initial_data.get('ingredients', [])
        tags = self.initial_data.get('tags', [])
        image = self.initial_data.get('image', None)

        if image is None or image == '' or (
            isinstance(image, str) and image.strip() == ''
        ):
            raise serializers.ValidationError({
                'image': ['Обязательное поле.']
            })
        if not ingredients:
            raise serializers.ValidationError(
                {'ingredients': ['Обязательное поле.']}
            )
        ingredient_ids = [item['id'] for item in ingredients]
        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise serializers.ValidationError(
                {'ingredients': ['Ингредиенты не должны повторяться.']}
            )
        existing_ingredients = Ingredient.objects.filter(id__in=ingredient_ids)
        if existing_ingredients.count() != len(ingredient_ids):
            raise serializers.ValidationError(
                {'ingredients': ['Указан несуществующий ингредиент.']}
            )
        if not tags:
            raise serializers.ValidationError(
                {'tags': ['Обязательное поле.']}
            )
        if len(tags) != len(set(tags)):
            raise serializers.ValidationError(
                {'tags': ['Теги не должны повторяться.']}
            )

        return data

    def _add_ingredients(self, ingredients_data, recipe):
        """Добавляет ингредиенты через bulk_create."""
        ingredient_ids = [item['id'] for item in ingredients_data]
        ingredients_map = {
            ingredient.id: ingredient
            for ingredient in Ingredient.objects.filter(id__in=ingredient_ids)
        }
        bulk_list = [
            IngredientInRecipe(
                ingredient=ingredients_map[item['id']],
                recipe=recipe,
                amount=item['amount']
            )
            for item in ingredients_data
        ]
        IngredientInRecipe.objects.bulk_create(bulk_list)

    def _update_relations(self, recipe, ingredients_data, tags):
        """Обновляет связи рецепта с ингредиентами и тегами."""
        IngredientInRecipe.objects.filter(recipe=recipe).delete()
        self._add_ingredients(ingredients_data, recipe)
        recipe.tags.set(tags)

    def create(self, validated_data):
        """Создаёт рецепт."""
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        user = self.context['request'].user
        recipe = Recipe.objects.create(author=user, **validated_data)
        self._update_relations(recipe, ingredients, tags)
        return recipe

    def update(self, instance, validated_data):
        """Обновляет рецепт."""
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance = super().update(instance, validated_data)
        self._update_relations(instance, ingredients, tags)
        return instance


class FollowCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания подписки."""

    class Meta:
        model = Follow
        fields = ()

    def validate(self, data):
        user = self.context['request'].user
        author = self.context['author']

        if user == author:
            raise serializers.ValidationError({
                'errors': 'Нельзя подписаться на самого себя.'
            })

        if Follow.objects.filter(user=user, author=author).exists():
            raise serializers.ValidationError({
                'errors': 'Вы уже подписаны на этого пользователя.'
            })

        return data

    def create(self, validated_data):
        user = self.context['request'].user
        author = self.context['author']
        return Follow.objects.create(user=user, author=author)


class FollowRepresentationSerializer(UserSerializer):
    """Сериализатор для модели Follow."""

    recipes = serializers.SerializerMethodField(
        read_only=True,
        method_name='get_recipes')
    recipes_count = serializers.IntegerField(
        read_only=True,
        default=0
    )

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'avatar', 'recipes', 'recipes_count',)

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes = obj.recipes.all()
        limit = request.query_params.get('recipes_limit')
        if limit and limit.isdigit():
            recipes = recipes[:int(limit)]

        return RecipeShortSerializer(
            recipes,
            many=True,
            context={'request': request}
        ).data


class AddFavoritesSerializer(RecipeShortSerializer):
    """Сериализатор для добавления в избранное."""
    pass
