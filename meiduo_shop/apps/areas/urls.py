from django.contrib.auth import logout
from django.urls import path

from apps.areas import views

urlpatterns = [
   path('areas/',views.AddressView.as_view()),
   path('areas/<id>/',views.SubaddressView.as_view()),
]
