import json
import uuid
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db import IntegrityError
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_list_or_404, get_object_or_404, render
from django.urls import reverse
from django.core.paginator import Paginator

from .models import Post, User, Follow


def index(request: HttpRequest) -> HttpResponse:
    """
    Home page view
    """
    # Get all posts
    posts = get_list_or_404(Post.objects.all().order_by("-timestamp"))
    # Paginate posts
    paginator = Paginator(posts, 10)
    page_number = request.GET.get("page")
    paginated_posts = paginator.get_page(page_number)
    return render(request, "network/index.html", {"posts": paginated_posts})


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


def user_profile(request: HttpRequest, username: str) -> HttpResponse:
    """
    User profile view with all posts by the user
    """
    user = get_object_or_404(User, username=username)
    posts = get_list_or_404(Post.objects.filter(user=user).order_by("-timestamp"))

    # Get the following status of the user
    followers = Follow.objects.filter(user_follower=user)
    following = Follow.objects.filter(user=user)

    #  Check if the current user is following when visitng the profile returning a boolean
    is_following = Follow.objects.filter(user=request.user, user_follower=user).exists()

    paginator = Paginator(posts, 10)
    page_number = request.GET.get("page")
    paginated_posts = paginator.get_page(page_number)

    return render(
        request,
        "network/profile.html",
        {
            "user": user,
            "posts": paginated_posts,
            "followers": followers,
            "following": following,
            "is_following": is_following,
        },
    )


def following(request: HttpRequest) -> HttpResponse:
    """
    Display all posts by users that the current user is following
    """
    current_user = get_object_or_404(User, username=request.user.username)
    following_object = get_list_or_404(Follow.objects.filter(user=current_user))
    posts = get_list_or_404(
        Post.objects.filter(
            user__in=[follow.user_follower for follow in following_object]
        ).order_by("-timestamp")
    )

    paginator = Paginator(posts, 10)
    page_number = request.GET.get("page")
    paginated_posts = paginator.get_page(page_number)

    return render(request, "network/following.html", {"posts": paginated_posts})


def follow(request: HttpRequest, user_follower: str) -> HttpResponse:
    """
    Follow a user profile with the given username
    """
    current_user = get_object_or_404(User, username=request.user.username)
    user_follower_object = get_object_or_404(User, username=user_follower)

    # Check if already following to avoid duplicate entries
    if not Follow.objects.filter(
        user=current_user, user_follower=user_follower_object
    ).exists():
        follow_object = Follow(user=current_user, user_follower=user_follower_object)
        follow_object.save()
        messages.success(request, "Followed successfully!")
    else:
        messages.error(request, "You are already following this user.")

    return HttpResponseRedirect(
        reverse("user_profile", kwargs={"username": user_follower})
    )


def unfollow(request: HttpRequest, user_follower: str) -> HttpResponse:
    """
    Unfollow a user profile with the given username
    """
    current_user = get_object_or_404(User, username=request.user.username)
    user_follower_object = get_object_or_404(User, username=user_follower)

    # Check if the follow relationship exists
    follow_relationship = Follow.objects.filter(
        user=current_user, user_follower=user_follower_object
    ).first()

    if follow_relationship:
        follow_relationship.delete()
        messages.success(request, "Unfollowed successfully!")
    else:
        messages.error(request, "You are not following this user.")

    return HttpResponseRedirect(
        reverse("user_profile", kwargs={"username": user_follower})
    )


def compose(request: HttpRequest) -> HttpResponse:
    """
    Compose a new post
    """
    if request.method == "POST":
        content = request.POST["content"]
        user = get_object_or_404(User, username=request.user.username)
        post = Post(content=content, user=user)
        post.save()
        set_alert_message(request, "Post created successfully!", messages.SUCCESS)
        return HttpResponseRedirect(reverse("index"))
    else:
        # If the request method is not POST, redirect back to index and show an error alert
        set_alert_message(request, "Invalid request method", messages.ERROR)
        return HttpResponseRedirect(reverse("index"))


def edit_post(request: HttpRequest, post_id: uuid) -> HttpResponse:
    """
    Edit a post
    """
    post = get_object_or_404(Post, id=post_id)
    if request.method == "POST":
        data = json.loads(request.body)
        print(f"view {data}")
        post.content = data["content"]
        post.save()
        set_alert_message(request, "Post updated successfully!", messages.SUCCESS)
        return JsonResponse(
            {"message": "Post updated successfully!", "data": post.content}
        )


def delete_post(request: HttpRequest, post_id: uuid) -> HttpResponse:
    """
    Delete a post
    """
    post = get_object_or_404(Post, id=post_id)
    if request.user == post.user:
        post.delete()
    set_alert_message(request, "Post deleted successfully!", messages.SUCCESS)
    return HttpResponseRedirect(reverse("index"))
