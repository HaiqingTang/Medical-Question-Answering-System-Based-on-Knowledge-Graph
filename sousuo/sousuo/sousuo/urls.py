"""sousuo URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from pathlib import Path
Path.joinpath(Path(__file__).resolve().parent.parent, 'main')
from main import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.homepage, name='homepage'),
    path('signUp/', views.signUp, name='signUp'),
    path('signIn/', views.signIn, name='signIn'),
    path('changePassword/', views.changePassword, name='changePassword'),
    path('myInfo/', views.myInfo, name='myInfo'),
    path('search/<str:question>/', views.searchResult, name='search'),
    path('discussion/', views.exchangeArea, name='discussion'),
    path('makePost/', views.makePost, name='makePost'),
    path('post/<int:postId>/', views.lookPost, name='post'),
    path('info/<int:uid>/', views.lookUserInfo, name='info'),
    path('myMark/', views.myMark, name='myMark'),
    path('myPosts/', views.myPosts, name='myPosts'),
    path('myFollow/', views.myFollow, name='myFollow'),
    path('sendMessage/<int:uid>/', views.sendMessage, name='sendMessage'),
    path('myMessage/', views.myMessage, name='myMessage'),
]
