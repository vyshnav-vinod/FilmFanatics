from django.urls import path
from . import views

app_name = "main"

urlpatterns = [
    path("", views.index, name="index"),
    path("register", views.register_view, name="register"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_user, name="logout"),
    path("add_movie", views.add_movie, name="addmovie"),
    path("profile/<int:pk>", views.profile, name="profile"),
    path("movie/<int:pk>", views.view_movie, name="viewmovie"),
    path("allmovies", views.list_movies, name="allmovies"),
    path("rate/<int:movie_id>", views.rate_movie, name="ratemovie"),
    path("addreview/<int:movie_id>", views.review_movie, name="reviewmovie")
]
