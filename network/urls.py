
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("post", views.post, name="post"),
    path("profile/<int:profile_id>/", views.profile, name="profile"),
    path("follow/<int:profile_id>/", views.follow, name="follow"),
    path("following", views.following, name="following"),
    path("edit/<int:post_id>", views.edit, name="edit"),
    path("toggle_like/<int:post_id>", views.toggle_like, name="toggle_like"),
    path("delete_post/<int:post_id>", views.delete_post, name="delete_post")
]
