from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Category(models.Model):
    name = models.CharField(max_length=250)

    def __str__(self) -> str:
        return self.name


class Movie(models.Model):
    title = models.CharField(max_length=250)
    description = models.TextField(max_length=5000)
    release_date = models.DateField()
    actors = models.CharField(max_length=500)
    poster = models.ImageField(upload_to="poster")
    trailer = models.URLField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.title
