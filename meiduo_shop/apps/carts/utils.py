import base64
import pickle

from django_redis import get_redis_connection


def merge_cookie_to_redis(request):
    #合并购物车
    user=request.user
    now_data = request.COOKIES.get('carts')
    if now_data:
        cookie_data = pickle.loads(base64.b64decode(now_data))
    else:
        return None
    client=get_redis_connection('carts')
    skus_hash=client.hgetall('carts_%s'%user.id)
    #获取redis里的sku_id
    sku_ids=[int(sku_id) for sku_id in skus_hash.keys()]
    pipe=client.pipeline()
    for sku_id,data in cookie_data.items():
        count = data['count']
        selected = data['selected']
        if sku_id in sku_ids:
            pipe.hset('carts_%s'%user.id,sku_id, count)
            if selected:
                pipe.sadd('selected_%s'%user.id,sku_id)
        else:
            pipe.hset('carts_%s'%user.id,sku_id,count)
            if selected:
                pipe.sadd('selected_%s'%user.id,sku_id)
    pipe.execute()
    return None