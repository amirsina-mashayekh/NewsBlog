from django.urls import path

from . import views

urlpatterns = [
    path('', views.Index, name='index'),
    path('news/<int:news_id>', views.FullNews, name='full_news'),
    path('archive', views.NewsArchive, name='news_archive'),
    path('signup', views.SignUp, name='signup'),
    path('login', views.Login, name='login'),
    path('logout', views.Logout, name='logout'),
]
