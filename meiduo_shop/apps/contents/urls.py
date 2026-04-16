from django.urls import path
from apps.contents import views
# Create your views here.
urlpatterns=[
    path('index/',views.IndexView.as_view()),
]