from django.contrib.auth.models import AbstractUser
from django.core.validators import (MaxValueValidator,
                                    MinValueValidator,
                                    RegexValidator,)
from django.db import models

from .constants import (EMAIL_LENGTH, FIRST_NAME_LENGTH,
                        INGREDIENT_MEASUREMENT_UNIT_LENGTH,
                        INGREDIENT_NAME_LENGTH, LAST_NAME_LENGTH,
                        MIN_AMOUNT_INGREDIENT, MIN_COOKING_TIME_VALUE,
                        RECIPE_NAME_LENGTH, TAG_NAME_LENGTH, TAG_SLUG_LENGTH,
                        MAX_COOKING_TIME_VALUE,
                        USERNAME_LENGTH)


class User(AbstractUser):
    """Кастомная модель пользователя для приложения foodgram."""

    email = models.EmailField(
        max_length=EMAIL_LENGTH,
        unique=True,
        verbose_name='Электронная почта'
    )

    username = models.CharField(
        max_length=USERNAME_LENGTH,
        unique=True,
        verbose_name='логин',
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+\Z',
                message=[
                    'Username может содержать только',
                    'буквы, цифры и @/./+/-/_'
                ]
            )
        ]
    )

    first_name = models.CharField(
        max_length=FIRST_NAME_LENGTH,
        verbose_name='Имя'
    )

    last_name = models.CharField(
        max_length=LAST_NAME_LENGTH,
        verbose_name='Фамилия'
    )

    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        verbose_name='Аватар',
        help_text='Рекомендуемый размер: 200x200 пикселей, формат— JPG или PNG'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('id',)

    def __str__(self):
        """Строковое представление объекта пользователя."""
        return self.username


class Tag(models.Model):
    """Модель для описания тега."""

    name = models.CharField(
        max_length=TAG_NAME_LENGTH,
        unique=True,
        verbose_name='Название тэга')

    slug = models.SlugField(
        max_length=TAG_SLUG_LENGTH,
        validators=[
            RegexValidator(
                regex=r'^[-a-zA-Z0-9_]+$',
                message=[
                    'Slug может содержать только латинские буквы,',
                    ' цифры, дефисы и подчеркивания.'
                ]
            )
        ],
        unique=True,
        verbose_name='Уникальный слаг')

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'slug'),
                name='unique_tags',
            ),
        )

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель для описания ингредиента."""

    name = models.CharField(
        max_length=INGREDIENT_NAME_LENGTH,
        db_index=True,
        verbose_name='Название ингредиента'
    )

    measurement_unit = models.CharField(
        max_length=INGREDIENT_MEASUREMENT_UNIT_LENGTH,
        verbose_name='Единицы измерения'
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Recipe(models.Model):
    """Модель для описания рецепта."""

    author = models.ForeignKey(
        User,
        related_name='recipes',
        on_delete=models.CASCADE,
        verbose_name='Автор',
    )
    name = models.CharField(
        max_length=RECIPE_NAME_LENGTH,
        verbose_name='Название'
    )
    image = models.ImageField(
        verbose_name='Изображение',
        upload_to='recipes/',
        blank=True,
        help_text='Максимальный размер — 5 МБ, формат — JPG, PNG'
    )
    text = models.TextField(
        verbose_name='Описание'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientInRecipe',
        related_name='recipes',
        verbose_name='Ингредиенты'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Теги'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        validators=[
            MinValueValidator(MIN_COOKING_TIME_VALUE),
            MaxValueValidator(MAX_COOKING_TIME_VALUE),
        ],
        help_text='Время приготовления в минутах'
    )
    created = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name='Дата публикации'
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-created',)

    def __str__(self):
        return self.name


class IngredientInRecipe(models.Model):
    """Промежуточная модель для ингредиентов в рецепте."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        verbose_name='Рецепт',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
        related_name='in_recipe'
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=[
            MinValueValidator(MIN_AMOUNT_INGREDIENT),
        ]
    )

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'
        constraints = [
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='unique_ingredients_in_the_recipe'
            )
        ]

    def __str__(self):
        return f'{self.ingredient} в {self.recipe}'


class ShoppingCart(models.Model):
    """Модель для описания формирования покупок."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_carts',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='in_shopping_carts',
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_shoppingcart'
            )
        ]

    def __str__(self):
        return f'{self.user} {self.recipe}'


class Favorite(models.Model):
    """Модель для создания избранного."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='in_favorites',
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_favorite'
            )
        ]

    def __str__(self):
        return f'{self.user} {self.recipe}'


class Follow(models.Model):
    """Модель для создания подписок на автора."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        related_name='followers',
        on_delete=models.CASCADE,
        verbose_name='Автор',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='unique_follow'
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F('author')),
                name='prevent_self_follow'
            )
        ]

    def __str__(self):
        return f'{self.user} подписан на {self.author}'
