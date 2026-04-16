from apps.carts import views
from django.urls import path
urlpatterns = [
    path('carts/', views.CartView.as_view()),
    path('carts/selection/',views.CartAllView.as_view()),
    path('carts/simple/', views.CartSimpleView.as_view()),
    path('orders/settlement/', views.OrderShowView.as_view()),
    path('orders/commit/',views.OrderCommitView.as_view()),
    # path('payment/status/',views.PaymentStatusView.as_view()),
    # path('payment/<order_id>/',views.PayUrlView.as_view()),
    path('carts/seckill/<int:product_id>',views.SeckillView.as_view()),
    path('carts/seckill_result/<int:product_id>',views.SeckillResultView.as_view()),
]