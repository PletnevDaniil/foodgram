import csv
from django.core.management.base import BaseCommand
from foodgram.settings import CSV_FILES_DIR
from recipes.models import Ingredient, Tag


class Command(BaseCommand):
    """Команда для загрузки ингредиентов и тегов в базу данных"""

    help = 'Загрузка данных из CSV файлов (ингредиенты и теги)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--ingredients',
            action='store_true',
            help='Загрузить только ингредиенты'
        )
        parser.add_argument(
            '--tags',
            action='store_true',
            help='Загрузить только теги'
        )

    def handle(self, *args, **options):
        load_ingredients = options['ingredients']
        load_tags = options['tags']

        load_all = not (load_ingredients or load_tags)

        if load_all or load_ingredients:
            self._import_ingredients()

        if load_all or load_tags:
            self._import_tags()

    def _import_ingredients(self):
        """Импорт ингредиентов из CSV"""
        try:
            with open(
                f'{CSV_FILES_DIR}/ingredients.csv',
                encoding='utf-8'
            ) as file:
                reader = csv.reader(file)
                next(reader)
                ingredients = [
                    Ingredient(
                        name=row[0],
                        measurement_unit=row[1],
                    )
                    for row in reader
                ]
                created_count = Ingredient.objects.bulk_create(ingredients)
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Успешно загружено {len(created_count)} ингредиентов'
                    )
                )
        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR('Файл ingredients.csv не найден')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Ошибка при загрузке ингредиентов: {str(e)}')
            )

    def _import_tags(self):
        """Импорт тегов из CSV"""
        try:
            with open(f'{CSV_FILES_DIR}/tags.csv', encoding='utf-8') as file:
                reader = csv.reader(file)
                created_count = 0
                for row in reader:
                    Tag.objects.get_or_create(
                        name=row[0],
                        slug=row[1]
                    )
                    created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Успешно загружено {created_count} тегов'
                    )
                )
        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR('Файл tags.csv не найден')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Ошибка при загрузке тегов: {str(e)}')
            )
