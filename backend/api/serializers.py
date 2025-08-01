from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from djoser.serializers import UserCreateSerializer

from drf_extra_fields.fields import Base64ImageField

from recipes.models import (
    Tag, Ingredient, Recipe, IngredientInRecipe,
    Follow, Favorite, ShoppingCart, User
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
    без проверки на подписку """

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

    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)
        super().__init__(*args, **kwargs)
        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

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
    """Сериализатор для ингредиентов в рецептах"""

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
    """Сериализатор для создания рецептов"""

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
        """Метод представления модели"""
        serializer = RecipeSerializer(
            instance,
            context={
                'request': self.context.get('request')
            }
        )
        return serializer.data

    def validate(self, data):
        """Основная валидация данных"""
        ingredients = self.initial_data.get('ingredients', [])
        tags = self.initial_data.get('tags', [])
        image = self.initial_data.get('image', None)

        if image is None or image == "" or (
            isinstance(image, str) and image.strip() == ""
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

    def create_ingredients(self, ingredients, recipe):
        ingredient_ids = [item['id'] for item in ingredients]
        ingredients_map = {
            ing.id: ing for ing in Ingredient.objects.filter(
                id__in=ingredient_ids
            )
        }

        bulk_list = []
        for item in ingredients:
            ingredient = ingredients_map.get(item['id'])
            if not ingredient:
                raise serializers.ValidationError(
                    {'ingredients': [
                        f'Ингредиент с id={item["id"]} не существует.'
                    ]}
                )
            bulk_list.append(
                IngredientInRecipe(
                    ingredient=ingredient,
                    recipe=recipe,
                    amount=item['amount']
                )
            )
        IngredientInRecipe.objects.bulk_create(bulk_list)

    def create_tags(self, tags, recipe):
        """Метод добавления тега"""
        recipe.tags.set(tags)

    def create(self, validated_data):
        """Метод создания модели"""
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')

        user = self.context.get('request').user
        recipe = Recipe.objects.create(**validated_data, author=user)
        self.create_ingredients(ingredients, recipe)
        self.create_tags(tags, recipe)
        return recipe

    def update(self, instance, validated_data):
        """Метод обновления модели"""
        IngredientInRecipe.objects.filter(recipe=instance).delete()

        self.create_ingredients(validated_data.pop('ingredients'), instance)
        self.create_tags(validated_data.pop('tags'), instance)

        return super().update(instance, validated_data)


class FollowSerializer(UserSerializer):
    """Сериализатор для модели Follow."""

    recipes = serializers.SerializerMethodField(
        read_only=True,
        method_name='get_recipes')
    recipes_count = serializers.SerializerMethodField(
        read_only=True
    )

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'avatar', 'recipes', 'recipes_count',)

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes = obj.recipes.all()
        limit = request.query_params.get('recipes_limit')
        if limit:
            try:
                recipes = recipes[:int(limit)]
            except (ValueError, TypeError):
                pass

        serializer = RecipeSerializer(
            recipes,
            many=True,
            fields=('id', 'name', 'image', 'cooking_time'),
            context={'request': request}
        )
        return serializer.data

    @staticmethod
    def get_recipes_count(obj):
        """Метод для получения количества рецептов"""
        return obj.recipes.count()


class AddFavoritesSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления в избранное по модели Recipe."""

    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
