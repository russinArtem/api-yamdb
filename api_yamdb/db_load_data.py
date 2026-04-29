'''Заливка данных из .csv в папке static/data в БД.

Это стоило мне всех нервов!
'''

import csv
import sqlite3
import os

import django
from django.contrib.auth import get_user_model
from django.db import models

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api_yamdb.settings')
django.setup()

from reviews.models import (
    Category,
    Genre,
    Title,
    GenreTitle,
    Review,
    Comment
)

User = get_user_model()


DATA_PATH = 'static/data/'
MODEL_FILE_MATCH = (
    # (Model, file)
    (Category, 'category.csv'),
    (Comment, 'comments.csv'),
    (GenreTitle, 'genre_title.csv'),
    (Genre, 'genre.csv'),
    (Review, 'review.csv'),
    (Title, 'titles.csv'),
    (User, 'users.csv'),
)


def model_db_fields(model):
    '''Возвращает список полей таблицы в БД, связанной с моделью'''
    fields_mapping = {}
    for field in model._meta.get_fields():
        if field.concrete and not isinstance(field, models.ManyToManyField):
            fields_mapping[field.name] = field.get_attname_column()[1]
        else:
            fields_mapping[field.name] = field.name
    return fields_mapping


# Подключение к БД.
connection = sqlite3.connect('db.sqlite3')
cursor = connection.cursor()

# Перебираем все таблицы и соответствующие csv файлы
for model, file_name in MODEL_FILE_MATCH:

    # Для каждой таблицы используем своё контекстное окно
    with open(DATA_PATH + file_name, 'r', encoding='utf-8') as file:
        content = csv.reader(file)
        # первая строка csv. Содержит заголовок
        csv_header = next(content)

        table_fields = model_db_fields(model)
        # Получаем кортеж полей, куда заинсертятся данные. get(column, column) - вымер
        inserted_fields = [table_fields.get(column, column) for column in csv_header]

        # Я ща помру.
        if model == User:
            pass
            # insert_command = f'''
            #     INSERT INTO {model._meta.db_table} ({', '.join(inserted_fields + ['password'])})
            #     VALUES({', '.join(['?'] * (len(inserted_fields) + 1))})
            # '''.replace('    ', '')
            # cursor.executemany(insert_command, (data + ['qwerty123'] for data in content))
        else:
            insert_command = f'''
                INSERT INTO {model._meta.db_table} ({', '.join(inserted_fields)})
                VALUES({', '.join(['?'] * len(inserted_fields))})
            '''.replace('    ', '')
            cursor.executemany(insert_command, content)


# Коммит выполняем только если всё залилось и программа не упала с ошибкой.
connection.commit()
connection.close()
