from django.urls import path, include
from . import views

app_name = "main"

urlpatterns = [
    path("", views.index, name="index"),
    path("register", views.register_view, name="register"),
    path("login", views.login_view, name="login"),
]
