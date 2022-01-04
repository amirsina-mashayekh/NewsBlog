from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404

from News.models import Post, Ad


SliderNewsCount = 3
LatestNewsCount = 10
PopularNewsCount = 5
NewsPerPage = 12
AdsCount = 2


def index(request):
    slider_news = Post.objects.order_by('-publishDate', '-importance', '-visits')[:SliderNewsCount]

    popular_news = Post.objects.order_by('-visits') \
                       .exclude(id__in=slider_news)[:PopularNewsCount]

    latest_news = Post.objects.order_by('-publishDate') \
                      .exclude(id__in=slider_news)  \
                      .exclude(id__in=popular_news)[:LatestNewsCount]

    ads = Ad.objects.all()[:AdsCount]

    return render(request, 'News/index.html', context={
        'slider_news': slider_news,
        'latest_news': latest_news,
        'popular_news': popular_news,
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
