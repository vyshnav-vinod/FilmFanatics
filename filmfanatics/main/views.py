from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.db.models import Q, Sum

from .models import Category, Movie, Avatar, Review

# Create your views here.

def index(request):
    return render(request, "index.html")

def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect("/")
        else:
            messages.error(request, "Invalid credentials")
            return render(request, "login.html")

    return render(request, "login.html")

def register_view(request):

    if request.method == "POST":
        firstname = request.POST["firstname"]
        lastname = request.POST["lastname"]
        username = request.POST["username"]
        email = request.POST["email"]
        password  = request.POST["password"]
        
        if User.objects.all().filter(username=username).exists():
            messages.error(request, "Username already exists")
            return render(request, "register.html")
        elif User.objects.all().filter(email=email).exists():
            messages.error(request, "Email already exists")
            return render(request, "register.html")
        else:
            user = User.objects.create_user(username=username, email=email, first_name=firstname, last_name=lastname, password=password)
            user.save()
            Avatar.objects.create(user=user).save()
            context = {
                'firstname' : firstname,
                'lastname' : lastname
            }
            return  render(request, "welcome.html", context)
    
    return render(request, "register.html")

def logout_user(request):
    logout(request)
    return render(request, "logout.html")


@login_required(login_url="/login")
def add_movie(request):
    # TODO: Maybe get a API for a list of actors to show when selecting the actors field

    if request.method == "POST":
        title = request.POST["title"]
        description = request.POST["description"]
        genre = request.POST["genre"]
        release_date = request.POST["release_date"]
        actors = request.POST["actors"]
        poster = request.FILES["poster"]
        trailer = request.POST["trailer"]

        category = Category.objects.get(name=genre)
        author = request.user

        movie = Movie(title=title, description=description, category=category, release_date=release_date, actors=actors, poster=poster, trailer=trailer, author=author)
        movie.save()
        return render(request, "add_movie_success.html")

    category_list = Category.objects.all()
    return render(request, "add_movie.html", {'categories': category_list})


@login_required(login_url="/login")
def profile(request, pk):
    """Profile page for others to view and also for user to edit profile"""
    if request.method == "POST":
        # Option to edit (Only show edit if current user is the one editing )
        pass

    # FOR Now let user choose from some default avatars and no option to add custom avatar

    user = User.objects.get(id=pk)
    user_movies = Movie.objects.all().filter(author=pk)
    return render(request, "profile.html", {"profile_user": user, "movies": user_movies})

def view_movie(request, pk):
    movie = Movie.objects.get(id=pk)
    return render(request, "view_movie.html", {"movie": movie})

def list_movies(request):
    genres = Category.objects.all()
    
    if request.method == "POST":
        search = request.POST["search"]
        genre = request.POST["genre"]
        search_filter = request.POST["filter"]
        # TODO: After rating and reviews implement filter searches
        if genre:
            movies = Movie.objects.filter(Q(title__contains=search) & Q(category__name=genre))
        else:
            movies = Movie.objects.filter(Q(title__contains=search))
        

        # Filters

        if search_filter:
            match search_filter:
                case "latest":
                    movies = movies.order_by("-release_date")
                case "oldest":
                    movies = movies.order_by("release_date")
                case "most_rated":
                    movies = movies.order_by("-rating")
                case "least_rated":
                    movies = movies.order_by("rating")
                    
    
    else:
        movies = Movie.objects.all().order_by("-added_on")
    
    return render(request, "movies.html", {"movies": movies, "genres": genres})


@login_required(login_url="/login")
def rate_movie(request, movie_id):
    # TODO: Fix the coloring
    # TODO: FIx the button coloring

    movie = Movie.objects.get(id=movie_id)
    reviews = Review.objects.all().filter(movie=movie)
    user = User.objects.get(id=request.user.id)
    has_rated = reviews.filter(user=user)
    if has_rated:
        has_rated = True
    else:
        has_rated =  False

    if request.method == "POST":
        rating = request.POST["rating"]
        user_rated = Review(user=request.user, movie=movie, rating=rating)
        user_rated.save()
        movie.rating = reviews.aggregate(Sum('rating'))['rating__sum'] / reviews.count()
        movie.save()
        return HttpResponseRedirect(f"/movie/{movie_id}")
    
    return render(request, "rate.html", {"has_rated": has_rated})


@login_required(login_url="/login")
def review_movie(request, movie_id):
    # TODO: Add in html the limit of words of review is 500
    if request.method == "POST":
        movie = Movie.objects.get(id=movie_id)
        review_content = request.POST["review"]
        try:
            review = Review.objects.filter(movie=movie).get(user=request.user.id)
            review.review = review_content
            review.save()
        except Review.DoesNotExist:
            review = Review(user=request.user, review=review_content, movie=movie)
            review.save()
    return HttpResponseRedirect(f"/movie/{movie_id}")
        
