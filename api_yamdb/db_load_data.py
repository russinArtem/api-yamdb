'''Заливка данных из .csv в папке static/data в БД.

Для работы нужно правильно заполнить MODEL_FILE_MATCH:

    Схема заполнения
    (Имя django приложения модели, Название модели, Имя .csv файла с данными)

    Путь хранения .csv файлов для наполнения БД:
        static/data/...

Запускать лучше из директории /api_yamdb

Это стоило мне половины всех нервов! (дважды)
'''

import csv
import os
from pathlib import Path
import sqlite3

import django
from django.apps import apps
from django.db import models


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api_yamdb.settings')
django.setup()

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / 'static/data/'

MODEL_FILE_MATCH = (
    # (App, Model, file)
    ('reviews', 'Category', 'category.csv'),
    ('reviews', 'Comment', 'comments.csv'),
    ('reviews', 'GenreTitle', 'genre_title.csv'),
    ('reviews', 'Genre', 'genre.csv'),
    ('reviews', 'Review', 'review.csv'),
    ('reviews', 'Title', 'titles.csv'),
    ('accounts', 'CustomUser', 'users.csv'),
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
for app, model_name, file_name in MODEL_FILE_MATCH:

    # Получаем модель
    model = apps.get_model(app_label=app, model_name=model_name)

    # Для каждой таблицы используем своё контекстное окно
    with open(DATA_PATH / file_name, 'r', encoding='utf-8') as file:
        content = csv.reader(file)
        # первая строка csv. Содержит заголовок
        csv_header = next(content)

        table_fields = model_db_fields(model)
        # Получаем кортеж полей, куда заинсертятся данные.
        inserted_fields = [
            # get(column, column) - вымер.
            table_fields.get(column, column)
            for column in csv_header
        ]

        insert_command = f'''
            INSERT INTO {model._meta.db_table} ({', '.join(inserted_fields)})
            VALUES({', '.join(['?'] * len(inserted_fields))})
        '''.replace('    ', '')
        cursor.executemany(insert_command, content)


# Коммит выполняем только если всё залилось и программа не упала с ошибкой.
connection.commit()
connection.close()
