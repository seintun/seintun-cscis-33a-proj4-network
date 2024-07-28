from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db import IntegrityError
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_list_or_404, get_object_or_404, render
from django.urls import reverse

from .models import Post, User


def index(request: HttpRequest) -> HttpResponse:
    """
    Home page view
    """
    # Get all posts
    posts = get_list_or_404(Post.objects.all().order_by("-timestamp"))
    return render(request, "network/index.html", {"posts": posts})


def set_alert_message(
    request: HttpRequest,
    message: str,
    level: int = messages.SUCCESS | messages.INFO | messages.WARNING | messages.ERROR,
) -> None:
    """
    Helper function to set an alert message to be displayed
    """
    messages.add_message(request, level, message)


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(
                request,
                "network/login.html",
                {"message": "Invalid username and/or password."},
            )
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(
                request, "network/register.html", {"message": "Passwords must match."}
            )

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(
                request, "network/register.html", {"message": "Username already taken."}
            )
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


def compose(request: HttpRequest) -> HttpResponse:
    """
    Compose a new post
    """
    if request.method == "POST":
        content = request.POST["content"]
        user = get_object_or_404(User, username=request.user.username)
        post = get_object_or_404(Post, user=user, content=content)
        post.save()
        set_alert_message(request, "Post created successfully!", messages.SUCCESS)
        return HttpResponseRedirect(reverse("index"))
    else:
        # If the request method is not POST, redirect back to index and show an error alert
        set_alert_message(request, "Invalid request method", messages.ERROR)
        return HttpResponseRedirect(reverse("index"))


def delete_post(request: HttpRequest, post_id: int) -> HttpResponse:
    """
    Delete a post
    """
    post = get_object_or_404(Post, id=post_id)
    if request.user == post.user:
        post.delete()
    set_alert_message(request, "Post deleted successfully!", messages.SUCCESS)
    return HttpResponseRedirect(reverse("index"))
