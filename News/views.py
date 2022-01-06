from datetime import datetime
import random

from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.shortcuts import render, get_object_or_404

from News.models import Post, Ad, Category

ImportantNewsCount = 3
LatestNewsCount = 10
PopularNewsCount = 10
NewsPerPage = 12
AdsCount = 3
PaginationCount = 7
NewsOrders = ['publish_date', 'accepted_comments', 'visits', 'importance']
for i in range(0, len(NewsOrders)):
    NewsOrders.append('-' + NewsOrders[i])


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


def DateFromStrOrDefault(string: str, date_format: str, default: datetime) -> datetime:
    try:
        return datetime.strptime(string, date_format)
    except ValueError:
        return default


def NewsArchive(request):
    today = datetime.now()
    start_date = DateFromStrOrDefault(request.GET.get('start_date', ''), '%Y-%m-%d', datetime.min)
    end_date = DateFromStrOrDefault(request.GET.get('end_date', ''), '%Y-%m-%d', today) \
        .replace(hour=23, minute=59, second=59, microsecond=999999)

    category = request.GET.get('category', '')

    search_for = request.GET.get('search', '')

    order = request.GET.get('order', '')
    if order not in NewsOrders:
        order = '-publish_date'

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

    categories = Category.objects.all()
    if category and categories.filter(url_name=category).exists():
        news = news.filter(category__url_name=category)

    filters = ''
    if order != '-publish_date':
        filters += f"&order={order}"
    if start_date != datetime.min:
        filters += f"&start_date={start_date.strftime('%Y-%m-%d')}"
    if end_date.date() != today.date():
        filters += f"&end_date={end_date.strftime('%Y-%m-%d')}"
    if category:
        f"&category={category}"
    if search_for:
        f"&search={search_for}"

    paginator = Paginator(news, NewsPerPage)
    page = paginator.get_page(page_number)
    for post in page:
        post.summary = post.GetSummary(250)

    ads = list(Ad.objects.all()[:AdsCount])
    random.shuffle(ads)

    return render(request, 'News/news-archive.html', context={
        'page': page,
        'filters': filters.rstrip('&'),
        'categories': categories,
        'ads': ads,
    })


def FullNews(request, news_id: int):
    post = get_object_or_404(Post, id=news_id)
    return render(request, 'News/full-news.html', {'post': post})
