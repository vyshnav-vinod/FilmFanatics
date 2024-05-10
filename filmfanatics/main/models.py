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


class Avatar(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    img = models.URLField(default="https://img.freepik.com/free-psd/3d-illustration-human-avatar-profile_23-2150671142.jpg?t=st=1715333046~exp=1715336646~hmac=e941db73c41712d97bfc01647685731931716d7f4460a130d20c786d0635a8f2&w=826")

