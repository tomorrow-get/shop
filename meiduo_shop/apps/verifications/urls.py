from django.urls import path

from apps.verifications.views import Imageview,Smsview

urlpatterns=[
    path('image_codes/<uuid:uuid>/',Imageview.as_view()),
    path('sms_codes/<mobile:mobile>/',Smsview.as_view()),
]