from apps.goods import views
from django.urls import path
urlpatterns = [
    path('list/<category>/skus/', views.IndexView.as_view()),
    path('hot/<cat_id>/', views.HotView.as_view()),
    # path('search/',views.SKUSearchview()),
    path('detail/<int:sku_id>/',views.DetailView.as_view()),
    path('detail/visit/<category_id>/',views.DetailVisitView.as_view()),
]