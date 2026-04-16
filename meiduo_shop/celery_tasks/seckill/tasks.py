# celery_tasks/seckill/tasks.py

from celery import shared_task
from django.db import transaction
from django_redis import get_redis_connection

from apps.carts.models import OrderInfo
from apps.goods.models import SKU

@shared_task(bind=True, max_retries=3)
def process_seckill(self, user_id, product_id):
    r = get_redis_connection("carts")
    stock_key=f"seckill:stock:{product_id}"
    try:

        with transaction.atomic():
            sku = SKU.objects.select_for_update().get(id=product_id)

            # 再次校验库存（兜底）
            if sku.stock <= 0:
                r.set(f"seckill:result:{user_id}:{product_id}", "fail")
                return "库存不足"

            # 幂等校验（防重复下单）
            if OrderInfo.objects.filter(user_id=user_id).exists():
                r.set(f"seckill:result:{user_id}:{product_id}", "fail")
                return "重复订单"

            sku.stock -= 1
            sku.save()

            OrderInfo.objects.create(
                user_id=user_id,
                total_count=1,
                total_amount=sku.price,
                freight=0,
                status=OrderInfo.ORDER_STATUS_ENUM["UNPAID"]
            )
        r.set(f"seckill:result:{user_id}:{product_id}", "success")
        return "success"

    except Exception as e:
        r.incr(stock_key)
        self.retry(exc=e, countdown=5)