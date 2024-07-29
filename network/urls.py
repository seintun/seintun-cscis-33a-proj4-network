from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("profile/<str:username>/", views.user_profile, name="user_profile"),
    path("compose", views.compose, name="compose"),
    path("delete_post/<uuid:post_id>/", views.delete_post, name="delete_post"),
    path("follow/<str:user_follower>/", views.follow, name="follow"),
    path("unfollow/<str:user_follower>/", views.unfollow, name="unfollow"),
]
