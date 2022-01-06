import datetime
import random

from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404

from News.models import Post, Ad


ImportantNewsCount = 3
LatestNewsCount = 6
PopularNewsCount = 6
NewsPerPage = 12
AdsCount = 3


def index(request):
    important_news = Post.objects.order_by('-publishDate__day', '-importance', '-visits')[:ImportantNewsCount]
    for news in important_news:
        news.summary = news.GetSummary(75)

    most_popular_news = Post.objects.order_by('-visits')\
        .filter(publishDate__month=datetime.datetime.now().month)[0]
    most_popular_news.summary = most_popular_news.GetSummary(100)
    popular_news = Post.objects.order_by('-visits') \
                       .exclude(id__in=important_news) \
                       .exclude(id=most_popular_news.id)[:PopularNewsCount]
    for news in popular_news:
        news.summary = news.GetSummary(50)

    latest_news = Post.objects.order_by('-publishDate') \
                      .exclude(id__in=important_news)  \
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


def newsList(request, page_number: int):
    news = Post.objects.all()
    paginator = Paginator(news, NewsPerPage)
    page = paginator.get_page(page_number)
    return render(request, 'News/news-list.html', {'posts': page})


def fullNews(request, news_id: int):
    post = get_object_or_404(Post, id=news_id)
    return render(request, 'News/full-news.html', {'post': post})
