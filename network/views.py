from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required


from .models import User, Post, Follow


def index(request):
    posts = Post.objects.all().order_by('-date')
    return render(request, "network/index.html", {
        'posts': posts,
        'prompt': True
    })


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
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
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
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")

@login_required
def post(request):
    if request.method=="POST":
        new_post = request.POST.get("post-input")
        Post.objects.create(
            content=new_post,
            author= request.user
        )
        messages.success(request, 'Post created')
        return redirect('index')
    return HttpResponseRedirect(reverse("index"))

def profile(request, profile_id):
    posted_user = get_object_or_404(User, pk=profile_id)
    posts = Post.objects.filter(author=posted_user).order_by('-date')

    follower_count = posted_user.current_followers.count()
    following_count = posted_user.currently_following.count()

    is_following = Follow.objects.filter(followed_by= request.user, being_followed=posted_user).exists()
    return render(request, "network/profile.html", {
        "posts": posts,
        "user_being_viewed": posted_user,
        "is_following": is_following,
        "follower_count": follower_count,
        "following_count": following_count
    })

def follow(request, profile_id):
    target_user = get_object_or_404(User, pk=profile_id)
    if request.method== "POST":
        follow, created = Follow.objects.get_or_create(followed_by=request.user, being_followed=target_user)
        if not created:
           follow.delete()
           messages.error(request, f'Unfollowed {target_user}')
        else:
           messages.success(request, f'Followed {target_user}')
        return redirect(reverse('profile', kwargs={'profile_id': target_user.pk}))

@login_required
def following(request):
    currently_following = request.user.currently_following.all()
    followed_users = [follow.being_followed for follow in currently_following]

    posts = Post.objects.filter(author__in=followed_users).order_by('-date')

    return render(request, "network/index.html", {
        'posts': posts,
        'prompt': False
    })