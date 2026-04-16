from django.contrib.auth import logout
from django.urls import path

from apps.oauth import views

urlpatterns = [
    path('qq/authorization/',views.QQOauthView.as_view()),
    path('oauth_callback/',views.QQLoginView.as_view()),
]
