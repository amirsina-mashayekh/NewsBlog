from datetime import datetime
import random

from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse

from News.forms import PostEditForm, SignUpForm, LoginForm, AdvancedSearchForm
from News.models import Post, Ad, Category, Comment

ImportantNewsCount = 3
LatestNewsCount = 10
PopularNewsCount = 10
NewsPerPage = 12
AdsCount = 3
PaginationCount = 7


def Index(request):
    important_news = Post.objects.order_by('-publish_date__day', '-importance', '-visits')[:ImportantNewsCount]
    for news in important_news:
        news.summary = news.GetSummary(75)

    most_popular_news = Post.objects.order_by('-visits') \
        .filter(publish_date__month=datetime.now().month)[0]
    most_popular_news.summary = most_popular_news.GetSummary(100)
    popular_news = Post.objects.order_by('-visits') \
                       .exclude(id__in=important_news) \
                       .exclude(id=most_popular_news.id)[:PopularNewsCount]
    for news in popular_news:
        news.summary = news.GetSummary(50)

    latest_news = Post.objects.order_by('-publish_date') \
                      .exclude(id__in=important_news) \
                      .exclude(id__in=popular_news) \
                      .exclude(id=most_popular_news.id)[:LatestNewsCount]
    for news in latest_news:
        news.summary = news.GetSummary(50)

    ads = list(Ad.objects.all()[:AdsCount])
    random.shuffle(ads)

    return render(request, 'News/index.html', context={
        'important_news': important_news,
        'latest_news': latest_news,
        'popular_news': popular_news,
        'most_popular_news': most_popular_news,
        'ads': ads,
    })


def NewsArchive(request):
    form = AdvancedSearchForm(request.GET)
    default_order = form['order'][0].data['value']

    search_for = ''
    start_date = None
    end_date = None
    order = ''
    category = None

    if form.is_valid():
        search_for = form.cleaned_data['search']
        start_date = form.cleaned_data['start_date']
        end_date = form.cleaned_data['end_date']
        order = form.cleaned_data['order']
        category = form.cleaned_data['category']

    today = datetime.now().date()
    if not start_date:
        start_date = datetime.min.date()
    if not end_date:
        end_date = today
    if not order:
        order = default_order

    page_number = request.GET.get('page', '')

    try:
        int(page_number)
    except ValueError:
        page_number = 1

    news = Post.objects.all()
    if 'comment' in order:
        news = news.annotate(accepted_comments=Count('comments', filter=Q(comments__is_accepted=True)))
    news = news.order_by(order).filter(
        Q(publish_date__gte=start_date) &
        Q(publish_date__lte=end_date) &
        (Q(title__icontains=search_for) | Q(article__icontains=search_for))
    )

    if category:
        news = news.filter(categories=category)

    filters = ''
    if order != default_order:
        filters += f"&order={order}"
    if start_date != datetime.min.date():
        filters += f"&start_date={start_date.strftime('%Y-%m-%d')}"
    if end_date != today:
        filters += f"&end_date={end_date.strftime('%Y-%m-%d')}"
    if category:
        filters += f"&category={category.id}"
    if search_for:
        filters += f"&search={search_for}"

    paginator = Paginator(news, NewsPerPage)
    page = paginator.get_page(page_number)
    for post in page:
        post.summary = post.GetSummary(250)

    ads = list(Ad.objects.all()[:AdsCount])
    random.shuffle(ads)

    return render(request, 'News/news-archive.html', context={
        'page': page,
        'filters': filters.rstrip('&'),
        'form': form,
        'ads': ads,
    })


def FullNews(request, news_id: int):
    post = get_object_or_404(Post, id=news_id)
    post.visits += 1
    post.save()

    category: Category = post.categories.first()
    if category:
        other_posts = category.posts.order_by('-publish_date')[:10]
    else:
        other_posts = Post.objects.order_by('-publish_date')[:10]

    ads = list(Ad.objects.all()[:AdsCount])
    random.shuffle(ads)

    return render(request, 'News/full-news.html', context={
        'post': post,
        'category': category,
        'other_posts': other_posts,
        'ads': ads,
    })


def SignUp(request):
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('profile')
    else:
        form = SignUpForm()

    return render(request, 'News/signup.html', context={'form': form})


def Login(request):
    redirect_path = request.GET.get('next')
    if not redirect_path or redirect_path == reverse('index'):
        redirect_path = 'profile'

    if request.user.is_authenticated:
        return redirect(redirect_path)

    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect(redirect_path)
    else:
        form = LoginForm()

    return render(request, 'News/login.html', context={'form': form})


def Logout(request):
    redirect_path = request.GET.get('next')
    if not redirect_path or redirect_path == reverse('profile'):
        redirect_path = 'index'
    if request.user.is_authenticated:
        logout(request)
    return redirect(redirect_path)


@login_required
def Profile(request):
    user = request.user
    latest_posts = user.posts.order_by('-publish_date')[:20]
    latest_comments_on_posts = \
        Comment.objects.filter(post__author_id=user.id, is_accepted=False)[:30]
    return render(request, 'News/profile.html', context={
        'user': user,
        'posts': latest_posts,
        'comments_on_posts': latest_comments_on_posts,
    })


@login_required
def NewPost(request):
    if request.method == 'POST':
        form = PostEditForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            form.save_m2m()
            return HttpResponseRedirect(reverse('full_news', args=[post.id]))
    else:
        form = PostEditForm()

    return render(request, 'News/post-editor.html', context={'form': form})


@login_required
def EditPost(request, news_id: int):
    post = get_object_or_404(Post, id=news_id)
    if request.user != post.author:
        raise PermissionDenied
    if request.method == 'POST':
        form = PostEditForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save()
            return HttpResponseRedirect(reverse('full_news', args=[post.id]))
    else:
        form = PostEditForm(instance=post)

    return render(request, 'News/post-editor.html', context={'form': form})


@login_required
def DeletePost(request, news_id: int):
    post = get_object_or_404(Post, id=news_id)
    if request.user != post.author:
        raise PermissionDenied
    post.delete()
    return redirect('profile')


@login_required
def AcceptComment(request, comment_id: int):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user != comment.post.author:
        raise PermissionDenied
    comment.is_accepted = True
    comment.save()
    return redirect('profile')


@login_required
def DeleteComment(request, comment_id: int):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user != comment.post.author:
        raise PermissionDenied
    comment.delete()
    return redirect('profile')
