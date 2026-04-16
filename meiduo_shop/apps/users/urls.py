from django.contrib.auth import logout
from django.urls import path

from apps.users import views

urlpatterns = [
    path('usernames/<username:username>/count/',views.UsernamecountView.as_view()),
    path('mobiles/<mobile:mobile>/count/',views.MobilecountView.as_view()),
    path('register/',views.RegisterView.as_view()),
    path('login/',views.LoginView.as_view()),
    path('logout/',views.LogoutView.as_view()),
    path('info/',views.CenterView.as_view()),
    path('emails/',views.EmailView.as_view()),
    path('emails/verification/',views.VerifyEmailView.as_view()),
    path('addresses/create/',views.AddressCreateView.as_view()),
    path('addresses/<int:address_id>/',views.AddressUpdateView.as_view()),
    path('addresses/',views.AddressView.as_view()),
    path('addresses/<int:address_id>/default/',views.AddressDefaultView.as_view()),
    path('addresses/<int:address_id>/title/',views.AddressTitleView.as_view()),
    path('browse_histories/',views.UserHistoryView.as_view()),
]
