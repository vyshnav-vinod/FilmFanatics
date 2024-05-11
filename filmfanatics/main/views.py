# TODO: Add edit buttons for  reviews
# TODO: Change user has not added movies and reviews yet to add a movie and add a review when profile is of current user
# TODO: Add a slide/carousal for added movies in profile

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponseForbidden
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


# @login_required(login_url="/login")
def profile(request, pk):
    """Profile page for others to view and also for user to edit profile"""
    if request.method == "POST":
        # Option to edit (Only show edit if current user is the one editing )
        pass

    # FOR Now let user choose from some default avatars and no option to add custom avatar

    user = User.objects.get(id=pk)
    user_movies = Movie.objects.all().filter(author=pk)
    user_reviews = Review.objects.filter(user=user).order_by("-added_on")
    return render(request, "profile.html", {"profile_user": user, "movies": user_movies, "reviews": user_reviews})

def view_movie(request, pk, _already_reviewed=False):
    # _already_reviewed is set to know if user has already reviewed it. It
    # is called from review_movie() only
    # TODO: Fix the position of the edit and dlt icon in reviews
    if _already_reviewed:
        messages.error(request, "You have already reviewed once!!")
    movie = Movie.objects.get(id=pk)
    reviews = Review.objects.filter(movie=movie).order_by("-added_on").filter(~Q(review=None))
    reviews_count = reviews.count()
    return render(request, "view_movie.html", {"movie": movie, "reviews": reviews, "count": reviews_count})

def list_movies(request):
    genres = Category.objects.all()
    
    if request.method == "POST":
        search = request.POST["search"]
        genre = request.POST["genre"]
        search_filter = request.POST["filter"]
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
    review = None
    try:
        review = Review.objects.filter(user=request.user).get(movie=movie)
        has_rated = True if review.rating > 0 else False
    except Review.DoesNotExist:
        has_rated = False

    if request.method == "POST":
        user_rating = request.POST["rating"]
        if review is None:
            # No rating or review done by user
            review = Review(movie=movie, user=request.user, rating=user_rating)
            review.save()
        else:
            review.rating = user_rating
            review.save()

        movie_reviews = Review.objects.filter(movie=movie)
        movie.rating = movie_reviews.aggregate(Sum('rating'))['rating__sum'] / movie_reviews.count()
        movie.save()

        return HttpResponseRedirect(f"/movie/{movie_id}")

    return render(request, "rate.html", {"has_rated": has_rated})


@login_required(login_url="/login")
def review_movie(request, movie_id):
    if request.method == "POST":
        movie = Movie.objects.get(id=movie_id)
        review_content = request.POST["review"]
        try:
            review = Review.objects.filter(movie=movie).get(user=request.user.id)
            if review.review:
                return view_movie(request, movie_id, _already_reviewed=True)
            review.review = review_content
            review.save()
        except Review.DoesNotExist:
            review = Review(user=request.user, review=review_content, movie=movie)
            review.save()
    return HttpResponseRedirect(f"/movie/{movie_id}")


@login_required(login_url="/login")
def dlt_movie(request, movie_id):
    if request.method == "POST":
        movie = Movie.objects.get(id=movie_id)
        if not request.user.id == movie.author.id:
            return HttpResponseForbidden("Forbidden")
        movie.delete()
        return HttpResponseRedirect("/")
    return HttpResponseForbidden("Forbidden")
    

@login_required(login_url="/login")
def dlt_review(request, movie_id):
    if request.method == "POST":
        movie = Movie.objects.get(id=movie_id)
        review = Review.objects.filter(movie=movie).get(user=request.user)
        if not request.user.id == review.user.id:
            return HttpResponseForbidden("Forbidden")
        review.delete()
        return HttpResponseRedirect(f"/movie/{movie_id}")
    return HttpResponseForbidden("Forbidden")
    
@login_required(login_url="/login")
def edit_profile(request, pk):
    if not request.user.id == pk:
        return HttpResponseForbidden("Forbidden")

    if request.method == "POST":
        # TODO: edit avatar
        # TODO: change password option
        username = request.POST["username"]
        firstname = request.POST["firstname"]
        lastname = request.POST["lastname"]

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken!!")
            return render(request, "edit_profile.html")

        user = User.objects.get(id=pk)
        user.username = username
        user.first_name = firstname
        user.last_name = lastname
        user.save()

        return HttpResponseRedirect(f"/profile/{pk}")
    
    avatars = ["https://img.freepik.com/free-psd/3d-illustration-human-avatar-profile_23-2150671142.jpg?t=st=1715333046~exp=1715336646~hmac=e941db73c41712d97bfc01647685731931716d7f4460a130d20c786d0635a8f2&w=826", 
               "https://img.freepik.com/free-psd/3d-illustration-person-with-sunglasses_23-2149436188.jpg?w=826&t=st=1715431551~exp=1715432151~hmac=2b0715fcae82a2483a29822218fa5256594d067639db97f3a828f027d8e9934a",
               "https://img.freepik.com/free-photo/androgynous-avatar-non-binary-queer-person_23-2151100226.jpg?t=st=1715431642~exp=1715435242~hmac=89534f023b56c20a1016d36367b8bc1103d25dc33196ba3635b902bbfc3aab57&w=826",
               "https://img.freepik.com/free-psd/3d-illustration-human-avatar-profile_23-2150671140.jpg?t=st=1715431656~exp=1715435256~hmac=9aa69c4b1309e39b971b59a415f97ba324ef178dd26bebcae635796dfe83fda6&w=826",
               "https://img.freepik.com/free-psd/3d-illustration-person-with-glasses_23-2149436185.jpg?t=st=1715431678~exp=1715435278~hmac=2b9bcaf02c39b95bd68acfca0d97d0c077b6a162171685d55cacd83b1459e118&w=826",
               "https://img.freepik.com/free-photo/3d-illustration-teenager-with-funny-face-glasses_1142-50955.jpg?t=st=1715431731~exp=1715435331~hmac=3731908b1bc463fb40417a9e53cdf41898d536e39cf5fd6b7735b99f8c461a34&w=826"]
    
    return render(request, "edit_profile.html", {"avatars": avatars})



@login_required(login_url="/login")
def edit_movie(request, movie_id):
    
    movie = Movie.objects.get(id=movie_id)
    if not request.user.id == movie.author.id:
        return HttpResponseForbidden("Forbidden")
    categories = Category.objects.all()

    if request.method == "POST":        
        poster = request.FILES["poster"] if request.FILES else  movie.poster
        title = request.POST["title"]
        description = request.POST["description"]
        actors = request.POST["actors"]
        release_date = request.POST["release_date"]
        trailer = request.POST["trailer"]
        genre = request.POST["genre"]

        movie.title = title
        movie.description = description
        movie.genre = genre
        movie.actors = actors
        movie.trailer = trailer
        movie.poster = poster
        movie.release_date = release_date
        movie.save()
        return HttpResponseRedirect(f"/movie/{movie_id}")


    return render(request, "edit_movie.html", {"movie": movie, "categories": categories})