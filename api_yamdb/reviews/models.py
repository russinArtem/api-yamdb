from datetime import date

from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .constants import (
    MAX_NAME_LENGTH,
    MAX_SLUG_LENGTH,
)

User = get_user_model()


class Category(models.Model):
    name = models.CharField(
        max_length=MAX_NAME_LENGTH,
        verbose_name='Категория'
    )
    slug = models.SlugField(
        max_length=MAX_SLUG_LENGTH,
        unique=True,
        verbose_name='Категория-слаг'
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(
        max_length=MAX_NAME_LENGTH,
        verbose_name='Жанр'
    )
    slug = models.SlugField(
        max_length=MAX_SLUG_LENGTH,
        unique=True,
        verbose_name='Жанр-слаг'
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name


class Title(models.Model):
    category = models.ForeignKey(
        Category,
        related_name='titles',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='Категория'
    )
    genre = models.ManyToManyField(
        Genre,
        related_name='titles',
        blank=True,
        verbose_name='Жанр'
    )
    name = models.CharField(
        max_length=MAX_NAME_LENGTH,
        verbose_name='Название'
    )
    year = models.SmallIntegerField(
        blank=True,
        null=True,
        verbose_name='Год выпуска',
        validators=(MaxValueValidator(date.today().year),)
    )
    description = models.TextField(
        blank=True,
        verbose_name='Описание'
    )

    class Meta:
        ordering = ('-year',)
        verbose_name = 'тайтл'
        verbose_name_plural = 'Тайтлы'

    def __str__(self):
        return self.name


class GenreTitle(models.Model):
    genre = models.ForeignKey(
        Genre,
        on_delete=models.CASCADE,
        verbose_name='Жанр'
    )
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        verbose_name='Тайтл'
    )

    class Meta:
        ordering = ('genre', 'title')
        verbose_name = 'связь жанра и тайтла'
        verbose_name_plural = 'Связи жанров и тайтлов'
        constraints = [
            models.UniqueConstraint(
                fields=('genre', 'title'),
                name='Unique constraint',
            ),
        ]

    def __str__(self):
        return f'{self.genre__name}: {self.title__name}'


class ContentModel(models.Model):
    """Родительский класс моделей контента."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
        db_index=True
    )
    text = models.TextField(
        verbose_name='Текст'
    )

    class Meta:
        abstract = True
        ordering = (
            '-pub_date',
            'author',
        )

    def __str__(self):
        return self.text


class Review(ContentModel):
    title = models.ForeignKey(
        Title,
        related_name='reviews',
        on_delete=models.CASCADE,
        verbose_name='Тайтл'
    )
    score = models.PositiveSmallIntegerField(
        validators=(
            MinValueValidator(1),
            MaxValueValidator(10),
        ),
        verbose_name='Оценка'
    )

    class Meta:
        ordering = (
            '-pub_date',
            'author',
        )
        verbose_name = 'отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = [
            models.UniqueConstraint(
                fields=('author', 'title'),
                name='unique_review_per_author'
            )
        ]


class Comment(ContentModel):
    review = models.ForeignKey(
        Review,
        related_name='comments',
        on_delete=models.CASCADE,
        verbose_name='Отзыв'
    )

    class Meta:
        ordering = (
            '-pub_date',
            'author',
        )
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'
