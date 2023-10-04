from django.urls import path

from . import views

urlpatterns = [
    path("", views.login, name="login"),
    path("connect", views.connect, name="connect"),
    path('redirect', views.callback, name="callback"),
    path('home', views.home, name="home"),
]