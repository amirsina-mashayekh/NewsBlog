from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('news/<int:news_id>', views.fullNews, name="new_passenger"),
    path('list/<int:page_number>', views.newsList, name="news_list"),
]
