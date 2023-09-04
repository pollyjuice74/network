from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.core.paginator import Paginator
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone
import json

from .forms import CommentForm
from .models import User, Post, Comment, CommentLike


def index(request):
    posts = Post.objects.all().order_by('-timestamp')
    paginator = Paginator(posts, 10)  # Display 10 posts per page

    return render(request, "network/index.html", {
        "posts": posts
    })


@login_required
def create_post(request):
    if request.method == 'POST':
        content = request.POST['content']
        author = request.user

        Post.objects.create(content=content, author=author)
        return redirect('index')

    return render(request, 'network/index.html')  # Render the same page if it's a GET request


@login_required
def create_comment(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(Post, id=post_id)
        content = request.POST.get('content')
        author = request.user
        
        comment = Comment(post=post, content=content, author=author)
        comment.save()
        
        # Optionally, you can return a JSON response indicating the success
        return JsonResponse({'message': 'Comment created successfully'})
    
    # Handle other HTTP methods or invalid requests if necessary
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def profile(request, user_id):

    # Get the user associated with the provided user_id
    profile_user = get_object_or_404(User, id=user_id)
    user = request.user

    # Get the posts for the profile user in reverse chronological order
    posts = Post.objects.filter(author=profile_user).order_by('-timestamp')

    # Determine if the current user is already following the profile user
    is_following = profile_user.followers.filter(id=user.id).exists()

    # Handle follow toggle
    if request.method == 'POST':
        if profile_user.followers.filter(id=user.id).exists():
            profile_user.followers.remove(user)
        else:
            profile_user.followers.add(user)
        is_following = not is_following

    return render(request, 'network/profile.html', {
        'profile_user': profile_user,
        'posts': posts,
        'is_following': is_following
    })


def following(request):
    following_users = request.user.following.all()
    posts = Post.objects.filter(author__in=following_users).order_by('-timestamp')

    paginator = Paginator(posts, 10)  # Display 10 posts per page
    page_number = request.GET.get('page')
    page_posts = paginator.get_page(page_number)

    return render(request, "network/index.html", {
        "posts": page_posts,
        })


@csrf_exempt
@login_required
def like_post(request, post_id, action):
    try: 
        post = Post.objects.get(pk=post_id)
        user = request.user

        if action == 'like':
            post.likes.add(user)
        elif action == 'unlike':
            post.likes.remove(user)
        else: 
            return JsonResponse({'status': 'success', 'message': 'Invalid action'})
        
        updated_likes_count = post.likes.count()
        return JsonResponse({'status': 'success', 'message': updated_likes_count})
    except Post.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Post not found'})


@csrf_exempt
@login_required  # Ensures the user is authenticated to access this endpoint
def edit_post(request, post_id):
    if request.method == 'POST':
        try:
            post = Post.objects.get(id=post_id, author=request.user)
            data = json.loads(request.body.decode('utf-8'))
            content = data.get('content', '')  

            # Update the post content
            post.content = content
            post.save()

            return JsonResponse({'status': 'success', 'content': post.content})
        except Post.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Post not found or you do not have permission to edit it.'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})


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

