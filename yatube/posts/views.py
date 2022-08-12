from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User

POSTS_ON_PAGE = 10


@cache_page(20, key_prefix='index_page')
def index(request):
    """View function for main page"""
    post_list = Post.objects.all()
    paginator = Paginator(post_list, POSTS_ON_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    """View function for group page"""
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    paginator = Paginator(post_list, POSTS_ON_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    """View function for profile page"""
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    paginator = Paginator(posts, POSTS_ON_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    total_posts = posts.count()

    follow_exists = Follow.objects.filter(
        author_id=author.id,
        user_id=request.user.id,
    ).exists()

    if follow_exists and request.user.is_authenticated():
        following = True
    else:
        following = False

    context = {
        'page_obj': page_obj,
        'total_posts': total_posts,
        'author': author,
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    """View function for post page"""
    post = get_object_or_404(Post, id=post_id)
    title = post.text[:30]
    author = post.author
    total_posts = author.posts.count()

    comment_form = CommentForm()
    comments = post.comments.all()
    context = {
        'post': post,
        'title': title,
        'total_posts': total_posts,
        'comment_form': comment_form,
        'comments': comments
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    """View function for post create page"""
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )

    if form.is_valid():
        non_author_post = form.save(commit=False)
        non_author_post.author = request.user
        non_author_post.save()
        return redirect('posts:profile', request.user)

    context = {
        'form': form,
        'is_edit': False
    }
    return render(request, 'posts/post_create.html', context)


@login_required
def post_edit(request, post_id):
    """View function for edit page"""
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return redirect('posts:post_detail', post_id)

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post,
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)

    context = {
        'form': form,
        'is_edit': True
    }
    return render(request, 'posts/post_create.html', context)


@login_required
def add_comment(request, post_id):
    """Function for comment saving"""
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    """The same as index page but only with following authors."""

    # I Don't really think it is perfect
    follows = Follow.objects.filter(user_id=request.user.id)
    ids = follows.values_list('author_id')

    posts = Post.objects.filter(author__id__in=ids)
    paginator = Paginator(posts, POSTS_ON_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj
    }
    return render(request, 'posts/follow_index.html', context)


@login_required
def profile_follow(request, username):
    user = get_object_or_404(User, username=username)
    does_exist = Follow.objects.filter(
        user=request.user,
        author=user,
    ).exists()
    if request.user != user and not does_exist:
        Follow.objects.create(
            user=request.user,
            author=user,
        )
    return redirect('posts:profile', username)


@login_required
def profile_unfollow(request, username):
    follow = Follow.objects.filter(
        user=request.user,
        author=get_object_or_404(User, username=username),
    )
    if follow.exists():
        follow.delete()
    return redirect('posts:profile', username)
