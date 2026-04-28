from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


User = get_user_model()


class Category(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Title(models.Model):
    category = models.ForeignKey(Category, related_name='titles', on_delete=models.SET_NULL, blank=True, null=True)
    genre = models.ManyToManyField(Genre, through='GenreTitle', related_name='titles', blank=True, null=True)
    name = models.CharField(max_length=256)
    year = models.IntegerField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class GenreTitle(models.Model):
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    title = models.ForeignKey(Title, on_delete=models.CASCADE)


class ContentModel(models.Model):
    """Родительский класс моделей контента."""

    author = models.ForeignKey(User, on_delete=models.CASCADE)
    pub_date = models.DateTimeField(verbose_name='Дата публикации', auto_now_add=True)
    text = models.TextField()

    class Meta:
        abstract = True
        ordering = (
            '-pub_date',
            'author',
        )

    def __str__(self):
        return self.text


class Review(ContentModel):
    title = models.ForeignKey(Title, related_name='rewiews', on_delete=models.CASCADE)
    score = models.IntegerField(
        validators=(
            MinValueValidator(1),
            MaxValueValidator(10),
        )
    )


class Comment(ContentModel):
    review = models.ForeignKey(Review, related_name='comments', on_delete=models.CASCADE)
