import json

from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

from .models import User, Post, Follow, Like


def index(request):
    posts = Post.objects.all().order_by('-date')
    paginator = Paginator(posts, 10)

    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    
    liked_posts = Like.objects.filter(liked_by= request.user, liked_post__in=posts).values_list('liked_post_id', flat=True)
    return render(request, "network/index.html", {
        'posts': posts,
        'liked_posts': liked_posts,
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

@login_required
@csrf_exempt
def edit(request, post_id):
    if request.method=="PUT":
        post = get_object_or_404(Post, id=post_id)
        if post.author != request.user:
            return JsonResponse({
                "error": "Must be author of the post"
            }, status=403)
    
        data = json.loads(request.body)
        new_content = data.get("newcontent")
        if new_content:
            post.content = new_content
            post.save()
            return JsonResponse({'success': True})
    else:
        return JsonResponse({
            "error": "Must be a PUT request"
        })

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

@login_required
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

@login_required
@csrf_exempt
def toggle_like(request, post_id):
    if request.method == "PUT":
        post = get_object_or_404(Post, pk=post_id)
        user = request.user

        like, created = Like.objects.get_or_create(liked_post=post, liked_by=user)
        if created:
            post.likes += 1
            message = "Liked"
        else:
            like.delete()
            post.likes -= 1
            message = "Unliked"
        post.save()
        print(post)
        return JsonResponse({
            'message': message,
            'likes': post.likes
        })
    return JsonResponse({'error': 'Invalid request method'}, status = 400)

