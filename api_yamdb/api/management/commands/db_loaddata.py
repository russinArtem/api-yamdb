"""Заливка данных из .csv в папке static/data в БД.

Для работы нужно правильно заполнить MODEL_FILE_MATCH:

    Схема заполнения
    (Название модели, Имя .csv файла с данными)

    Путь хранения .csv файлов для наполнения БД:
        static/data/...

Запускать командой:
    python manage.py db_loaddata

Это стоило мне половины всех нервов! (трижды....)
"""
import csv
from pathlib import Path

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction

from reviews.models import (
    Category,
    Genre,
    Title,
    GenreTitle,
    Review,
    Comment
)

User = get_user_model()


BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
DATA_PATH = BASE_DIR / 'static/data/'

MODEL_FILE_MATCH = (
    # (Model, file)
    (User, 'users.csv'),

    (Category, 'category.csv'),
    (Comment, 'comments.csv'),
    (GenreTitle, 'genre_title.csv'),
    (Genre, 'genre.csv'),
    (Review, 'review.csv'),
    (Title, 'titles.csv'),
)


class Command(BaseCommand):

    help = 'Insert data from static/*.csv into DataBase.'

    @transaction.atomic
    def handle(self, *args, **options):

        for model, file_name in MODEL_FILE_MATCH:
            with open(DATA_PATH / file_name, 'r', encoding='utf-8') as file:
                content = csv.DictReader(file)
                for data_row in content:
                    # Заплатки
                    if 'author' in data_row:
                        user_id = data_row.get('author')
                        data_row['author'] = User.objects.get(
                            id=user_id
                        )
                    if 'category' in data_row:
                        category_id = data_row.get('category')
                        data_row['category'] = Category.objects.get(
                            id=category_id
                        )
                    model(**data_row).save(force_insert=True)
            self.stdout.write(
                self.style.SUCCESS(
                    (
                        f'Successfully imported data from '
                        f'{file_name} to {model._meta.db_table}'
                    )
                )
            )
