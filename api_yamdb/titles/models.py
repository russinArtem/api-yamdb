from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


User = get_user_model()


class Categories(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Genres(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Titles(models.Model):
    category = models.ForeignKey(Categories, related_name='titles', on_delete=models.SET_NULL, blank=True, null=True)
    genre = models.ManyToManyField(Genres, through='GenreTitle', related_name='titles')
    name = models.CharField(max_length=256)
    year = models.IntegerField()
    description = models.TextField()

    def __str__(self):
        return self.name


class GenreTitle(models.Model):
    genre = models.ForeignKey(Genres, on_delete=models.CASCADE)
    title = models.ForeignKey(Titles, on_delete=models.CASCADE)


class ContentModel(models.Model):
    """Родительский класс моделей контента."""

    author = models.ForeignKey(User, related_name='rewiews', on_delete=models.CASCADE)
    pub_date = models.DateTimeField(verbose_name='Дата публикации', auto_now_add=True)
    text = models.TextField()

    class Meta:
        ordering = (
            '-pub_date',
            'author',
        )

    def __str__(self):
        return self.text


class Reviews(ContentModel):
    title = models.ForeignKey(Titles, related_name='rewiews', on_delete=models.CASCADE)
    score = models.IntegerField(
        validators=(
            MinValueValidator(1),
            MaxValueValidator(10),
        )
    )


class Comments(ContentModel):
    review = models.ForeignKey(Reviews, related_name='comments', on_delete=models.CASCADE)
