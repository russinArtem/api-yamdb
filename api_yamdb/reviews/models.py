from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.TextField()
    year = models.IntegerField()
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, related_name='titles')
    genre = models.ManyToManyField(Genre, related_name='titles', blank=True)

    def __str__(self):
        return self.name
