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
    path("addreview/<int:movie_id>", views.review_movie, name="reviewmovie"),
    path("edit/movie/<int:movie_id>", views.edit_movie, name="editmovie"),
    # path("edit/profile/<int:pk>", views.edit_movie, name="editprofile"),
    # path("edit/review/<int:pk>", views.edit_movie, name="editreview"),
    path("delete/movie/<int:movie_id>", views.dlt_movie, name="dltmovie"),
    # path("delete/profile/<int:pk>", views.dlt_movie, name="dltprofile"),
    # path("delete/review/<int:pk>", views.dlt_movie, name="dltreview"),



]
