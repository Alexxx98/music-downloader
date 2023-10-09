from django.urls import path

from . import views

urlpatterns = [
    path("", views.connect, name="connect"),
    path("login", views.login, name="login"),
    path('redirect', views.callback, name="callback"),
    path('home', views.home, name="home"),
]