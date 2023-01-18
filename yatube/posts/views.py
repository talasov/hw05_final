from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.conf import settings

from .models import Group, Post, User, Follow
from .forms import CommentForm, PostForm
from .utils import get_page

User = get_user_model()


def index(request):
    """Вывод постов на главную"""
    post_list = Post.objects.select_related('group')

    page_obj = get_page(post_list, request)
    context = {
        'page_obj': page_obj
    }
    return render(request, 'posts/index.html',
                  context)


def group_posts(request, slug):
    """Получение постов по группам"""
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    page_obj = get_page(post_list, request)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html',
                  context)


def profile(request, username):
    """ Получение постов по авторам """

    author = get_object_or_404(User, username=username)
    post_list = author.posts.all()
    page_obj = get_page(post_list, request)

    context = {
        'author': author,
        'posts': post_list,
        'page_obj': page_obj,
    }
    return render(request, 'posts/profile.html',
                  context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.filter(active=True)
    form = CommentForm()
    template = 'posts/post_detail.html'
    context = {
        'post': post,
        'requser': request.user,
        'comments': comments,
        'form': form,
    }
    return render(request, template, context)


@login_required
def post_create(request):
    '''Создание поста'''
    if request.method == "POST":
        form = PostForm(request.POST, files=request.FILES)

        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect("posts:profile", request.user.username)
    else:
        form = PostForm()
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    '''Редактирование поста'''
    post = get_object_or_404(Post, pk=post_id)
    if post.author.pk == request.user.pk:
        if request.method == "POST":
            form = PostForm(request.POST, instance=post, files=request.FILES)
            if form.is_valid():
                post = form.save(commit=False)
                post.author = request.user
                post.save()
                return redirect('posts:post_detail', post.pk)
        else:
            form = PostForm(instance=post)
        return render(request, 'posts/create_post.html',
                      {'form': form, 'post': post, 'is_edit': True})


@login_required
def add_comment(request, post_id):
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
    posts = Post.objects.filter(
        author__following__user=request.user)
    paginator = Paginator(posts, settings.QUANTITY_POST)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj}
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if author != request.user:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('posts:profile', author)


@login_required
def profile_unfollow(request, username):
    follow = get_object_or_404(
        Follow,
        user=request.user,
        author__username=username
    )
    follow.delete()
    return redirect('posts:profile', username)
