from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import render
from django.http import HttpResponseRedirect

# Create your views here.

def index(request):
    return render(request, "index.html")

def login_view(request):
    # TODO: Create a user index page (user base html as well)
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
            context = {
                'firstname' : firstname,
                'lastname' : lastname
            }
            return  render(request, "welcome.html", context)
    
    return render(request, "register.html")