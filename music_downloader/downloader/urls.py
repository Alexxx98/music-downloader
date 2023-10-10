from django.urls import path

from . import views

urlpatterns = [
    path("", views.connect, name="connect"),
    path("login", views.login, name="login"),
    path('redirect', views.callback, name="callback"),
    path('home', views.home, name="home"),
    path('home/<int:playlist_id>', views.playlist_view, name="playlist_view"),
    path('download/<int:playlist_id>/<str:songs>', views.download, name="download"),
    path('success', views.success, name="success")
]