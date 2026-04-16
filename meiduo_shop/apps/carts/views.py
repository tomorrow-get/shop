import json
import time

from django.db import transaction
from django.http import JsonResponse
from django.db.models import F
from django.views import View

import pickle
import base64

from apps.carts.models import OrderInfo, OrderGoods
from apps.goods.models import SKU
from django_redis import get_redis_connection

from apps.users.models import Address
from utils.views import LoginRequiredJsonMixin


# Create your views here.
class CartView(View):
    def post(self, request):
        data = json.loads(request.body.decode())
        sku_id = data.get('sku_id')
        count = data.get('count')
        try:
            obj=SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return JsonResponse({'code':400,'errmsg':'商品已被下架'})
        user=request.user
        try:
            count=int(count)
        except Exception as e:
            count=1

        if user.is_authenticated:
            #用户已经登录,数据入redis
            client=get_redis_connection('carts')
            data=client.hget('carts_%s'%user.id,sku_id)
            if data :
                count+=int(data)
            client.hset('carts_%s'%user.id,sku_id,count)
            #默认该数据是选中状态
            client.sadd('selected_%s'%user.id,sku_id)
            return JsonResponse({'code': 0, 'errmsg': 'ok'})
        else:
            now_carts=request.COOKIES.get('carts')
            carts={}
            if now_carts:
                #解码现有数据
                carts = pickle.loads(base64.b64decode(now_carts))
            if sku_id in carts:
                carts[sku_id]['count']+=count
            else:
                carts[sku_id] = {'count':count,'selected':True}
            # #数据入cookie
            # carts={
            #     sku_id:{'count':count,'selected':True}
            # }

            data=pickle.dumps(carts)
            now=base64.b64encode(data)
            responses=JsonResponse({'code': 0, 'errmsg': 'ok'})
            responses.set_cookie('carts',now.decode(),max_age=3600*24*30)
            return responses
    def get(self, request):
        user=request.user
        if user.is_authenticated:
            #已经登录用户从redis里查
            client_redis=get_redis_connection('carts')
            cart_skus=[]
            '''
            cart_skus={'selected':True,'amount':2,'price':333}
            '''
            #获得的是哈希表key:sku_id value:count
            skus_id=client_redis.hgetall('carts_%s'%user.id)
            select_sku=client_redis.smembers('selected_%s'%user.id)
            sku_list=list(map(int,skus_id.keys()))
            skus=SKU.objects.filter(id__in=sku_list)
            sku_dict={sku.id:sku for sku in skus}
            for sku_id,count in skus_id.items():
                try:
                    sku = sku_dict.get(int(sku_id))
                    if sku is None:
                        continue
                    price = sku.price
                    if sku_id in select_sku:
                        selected = True
                    else:
                        selected = False
                    data = {
                        'id': int(sku_id),
                        'count': int(count),
                        'price': price,
                        'selected': selected,
                        'name': sku.name,
                        'default_image_url': sku.default_image.url,
                        'amount': price * int(count),
                    }
                    cart_skus.append(data)
                except SKU.DoesNotExist:
                    continue
            return JsonResponse({'code': 0, 'errmsg': 'ok', 'cart_skus': cart_skus})
        else:
            now_data=request.COOKIES.get('carts')
            if now_data:
                cookie_data = pickle.loads(base64.b64decode(now_data))
            else:
                cookie_data={}
            '''
            cookie中数据的形式
            carts={
                sku_id:{'count':count,'selected':True}
                sku_id:{'count':count,'selected':True}
            }
            '''
            cart_skus = []
            sku_list=list(map(int,cookie_data.keys()))
            skus = SKU.objects.filter(id__in=sku_list)
            sku_dict = {sku.id: sku for sku in skus}
            for sku_id,data in cookie_data.items():
                try:
                    sku = sku_dict.get(int(sku_id))
                    if sku is None:
                        continue
                    test_data = {
                        'id': int(sku_id),
                        'count': int(data['count']),
                        'price': sku.price,
                        'selected': data['selected'],
                        'name':sku.name,
                        'default_image_url':sku.default_image.url,
                        'amount':sku.price*data['count'],
                    }
                    cart_skus.append(test_data)
                except SKU.DoesNotExist:
                    continue
            return JsonResponse({'code': 0, 'errmsg': 'ok', 'cart_skus': cart_skus})
    def delete(self, request):
        data=json.loads(request.body.decode())
        sku_id=data.get('sku_id')
        user=request.user
        # try:删除操作不用考虑商品是否存在，都要删除
        #     sku = SKU.objects.get(id=sku_id)
        # except SKU.DoesNotExist:
        #     return JsonResponse({'code': 400, 'errmsg': '商品已经下架'})
        if user.is_authenticated:
            #已登录用户
            client=get_redis_connection('carts')
            selected_sku=client.smembers('selected_%s'%user.id)
            if str(sku_id).encode() in selected_sku:
                client.srem('selected_%s'%user.id,sku_id)
            client.hdel('carts_%s'%user.id,sku_id)
            return JsonResponse({'code': 0, 'errmsg': 'ok'})
        else:
            now_data = request.COOKIES.get('carts')
            if now_data:
                cookie_data = pickle.loads(base64.b64decode(now_data))
            else:
                cookie_data = {}
            cookie_data.pop(sku_id,None)
            responses=JsonResponse({'code': 0, 'errmsg': 'ok'})
            responses.set_cookie('carts', base64.b64encode(pickle.dumps(cookie_data)).decode(),max_age=3600*24*30)
            return responses
    def put(self, request):
        data=json.loads(request.body.decode())
        sku_id=data.get('sku_id')
        count=data.get('count')
        select_sku=data.get('selected')
        if not all([sku_id,count]):
            return JsonResponse({'code':400,'errmsg':'参数不全'})
        try:
            sku = SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return JsonResponse({'code': 400, 'errmsg': '没有此商品'})
        try:
            count=int(count)
        except Exception as e:
            count=1
        user=request.user
        if user.is_authenticated:
            client=get_redis_connection('carts')
            if select_sku is False:
                client.srem('selected_%s'%user.id,sku_id)
            elif select_sku is True:
                client.sadd('selected_%s'%user.id,sku_id)
            client.hset('carts_%s'%user.id,sku_id,count)
            return JsonResponse({'code': 0, 'errmsg': 'ok','cart_sku':{'count':count,'selected':select_sku}})
        else:
            now_data = request.COOKIES.get('carts')
            if now_data:
                cookie_data = pickle.loads(base64.b64decode(now_data))
            else:
                cookie_data = {}
            try:
                #更新数据
                cookie_data[sku_id]['count']=count
                cookie_data[sku_id]['selected']=select_sku
                response = JsonResponse({'code': 0, 'errmsg': 'ok', 'cart_sku': {'count':count,'selected':select_sku}})
                response.set_cookie('carts',base64.b64encode(pickle.dumps(cookie_data)).decode(), max_age=3600*24*30)
                return response
            except Exception as e:
                return JsonResponse({'code':400,'errmsg':'数据缓存被删除'})
class CartAllView(View):
    def put(self, request):
        data=json.loads(request.body.decode())
        selected=data.get('selected')
        user=request.user
        if user.is_authenticated:
            client=get_redis_connection('carts')
            pipe=client.pipeline()
            sku_ids=client.hgetall('carts_%s'%user.id)
            selected_sku_ids=pipe.smembers('selected_%s'%user.id)
            if selected:
                for sku_id, count in sku_ids.items():
                    if sku_id not in selected_sku_ids:
                        pipe.sadd('selected_%s'%user.id,sku_id)
            else:
                pipe.delete('selected_%s'%user.id)
            pipe.execute()
            return JsonResponse({'code': 0, 'errmsg': 'ok'})
        else:
            now_data = request.COOKIES.get('carts')
            if now_data:
                cookie_data = pickle.loads(base64.b64decode(now_data))
            else:
                cookie_data = {}

                '''
                cookie中数据的形式
                  carts={
                    sku_id:{'count':count,'selected':True}
                     sku_id:{'count':count,'selected':True}
                  }
                  '''
            for sku_id, data in cookie_data.items():
                if data['selected'] != selected:
                    cookie_data[sku_id]['selected']=selected
            responses = JsonResponse({'code': 0, 'errmsg': 'ok'})
            responses.set_cookie('carts', base64.b64encode(pickle.dumps(cookie_data)).decode(), max_age=3600 * 24 * 30)
            return responses
class CartSimpleView(View):
    def get(self, request):
        user=request.user
        cart_skus=[]
        if user.is_authenticated:
            client=get_redis_connection('carts')
            sku_ids=client.hgetall('carts_%s'%user.id)
            sku_list=list(map(int,sku_ids.keys()))

            skus = SKU.objects.filter(id__in=sku_list)
            sku_dict = {sku.id: sku for sku in skus}
            for sku_id, count in sku_ids.items():
                try:
                    sku=sku_dict.get(int(sku_id))
                    if sku is None:
                        continue
                except SKU.DoesNotExist:
                    continue
                test={'id':int(sku_id),
                      'count':int(count),
                      'name':sku.name,
                      'price':sku.price,
                      'default_image_url':sku.default_image.url,
                      }
                cart_skus.append(test)
            return JsonResponse({'code': 0, 'errmsg': 'ok', 'cart_skus':cart_skus})
        else:
            now_data = request.COOKIES.get('carts')
            if now_data:
                cookie_data = pickle.loads(base64.b64decode(now_data))
            else:
                cookie_data = {}
            sku_list = list(map(int, cookie_data.keys()))
            skus = SKU.objects.filter(id__in=sku_list)
            sku_dict = {sku.id: sku for sku in skus}
            for sku_id, data in cookie_data.items():
                try:
                    sku=sku_dict.get(int(sku_id))
                    if sku is None:
                        continue
                except SKU.DoesNotExist:
                    continue
                test={'id':int(sku_id),
                      'name':sku.name,
                      'price':sku.price,
                      'default_image_url':sku.default_image.url,
                      'count':data['count'],}
                cart_skus.append(test)
            return JsonResponse({'code': 0, 'errmsg': 'ok', 'cart_skus': cart_skus})
class OrderShowView(LoginRequiredJsonMixin,View):
    def get(self, request):
        '''
        context{'skus':[{‘id’:id...}...],'freight':freight,'addresses':addresses}
        '''
        user=request.user
        if user.is_authenticated:
            context={}
            address = Address.objects.filter(user=user, is_deleted=False)
            addresses = [{'id': new_address.id,
                          'title': new_address.title,
                          'receiver': new_address.receiver,
                          'province': new_address.province.name,
                          'city': new_address.city.name,
                          'district': new_address.district.name,
                          'place': new_address.place,
                          'tel': new_address.tel,
                          'email': new_address.email,
                          'mobile': new_address.mobile} for new_address in address if new_address is not None]
            context['addresses'] = addresses
            client=get_redis_connection('carts')
            sku_ids_byte=client.hgetall('carts_%s'%user.id)
            sku_count={}
            for sku_id, count in sku_ids_byte.items():
                sku_count[int(sku_id)]=int(count)
            selected_sku_ids=client.smembers('selected_%s'%user.id)
            sku_list=[int(sku_id) for sku_id in selected_sku_ids]
            sku_q=SKU.objects.filter(id__in=sku_list)
            sku_dict={sku.id:sku for sku in sku_q}
            skus_l=[]
            for sku_id,sku in sku_dict.items():
                count=sku_count.get(sku_id)
                data={
                    'id':sku_id,
                    'name':sku.name,
                    'price':sku.price,
                    'default_image_url':sku.default_image.url,
                    'count':count,
                }
                skus_l.append(data)
            from decimal import Decimal
            freight=Decimal('10')
            context['skus']=skus_l
            '''运费固定7元'''
            context['freight']=freight
            return JsonResponse({'code': 0, 'errmsg': 'ok', 'context':context})
        else:
            return JsonResponse({'code': 400, 'errmsg': '请先用户登录'})
'''
1. READ UNCOMMITTED（读未提交:允许读取其他事务未提交的数据） 
    允许读取其他事务未提交的数据，可能出现脏读、不可重复读、幻读。几乎不加锁，并发性能最高，但数据一致性最差。
    适用场景：极少使用，仅在对数据准确性要求极低的实时统计中考虑。

2. READ COMMITTED（读已提交:只能读取已提交数据）
    只能读取已提交数据，避免脏读，但可能出现不可重复读、幻读。多数数据库（Oracle、PostgreSQL）默认此级别。
    适用场景：需要实时读取最新提交数据且能容忍不可重复读的业务，如订单状态查询。

3. REPEATABLE READ（可重复读，MySQL默认） 
    无论其他事务是否修改数据，本事务读取的数据始终不变，不受其他事务影响
    同一事务内多次读取同一行结果一致，避免脏读和不可重复读。InnoDB通过MVCC快照读和Next-Key Lock大幅减少幻读。
    适用场景：大多数OLTP系统，如财务对账、库存管理，兼顾一致性与性能。

4. SERIALIZABLE（可串行化） 
    最高隔离级别，事务串行执行，完全避免脏读、不可重复读、幻读，但并发性能最低。
'''
class OrderCommitView(LoginRequiredJsonMixin,View):
    def post(self, request):
        '''发送过来多次请求怎么保证幂等性
        客户端在提交订单时，生成一个唯一的 idempotent_key，后端保存起来，
        对于新来的请求若redis里已有idempotent_key则直接返回
        '''
        data=json.loads(request.body.decode())
        address_id=data.get('address_id')
        pay_method=data.get('pay_method')
        if not all([address_id,pay_method]):
            return JsonResponse({'code':400,'errmsg':'参数缺失'})
        user=request.user
        try:
            address=Address.objects.get(id=address_id,user=user)
        except Address.DoesNotExist:
            return JsonResponse({'code': 400, 'errmsg': '地址不正确'})
        if pay_method not in [1,2]:
            return JsonResponse({'code': 400, 'errmsg': '参数不正确'})
        from django.utils import timezone
        order_id=timezone.localtime().strftime('%Y%m%d%H%M%S')+'%09d'%user.id
        if pay_method==1:
            pay_status=2#待支付
        else:
            pay_status=1#待发货
        total_count=0
        from decimal import Decimal
        total_amount=Decimal('0')
        freight=Decimal('10')
        with transaction.atomic():
            point=transaction.savepoint()
            try:
                orderinfo = OrderInfo.objects.create(
                    order_id=order_id,
                    user=user,
                    address=address,
                    total_count=total_count,
                    total_amount=total_amount,
                    freight=freight,
                    pay_method=pay_method,
                    status=pay_status,
                )
            except Exception as e:
                return JsonResponse({'code': 400, 'errmsg': '正在处理订单，稍后重试'})
            client = get_redis_connection('carts')
            selected_sku_ids = client.smembers('selected_%s' % user.id)
            # 获取哈希数据方便获取每件商品具体数量
            sku_carts = client.hgetall('carts_%s' % user.id)
            sku_data = {int(sku_id): int(count) for sku_id, count in sku_carts.items()}
            sku_list = [int(sku_id) for sku_id in selected_sku_ids]
            #通过排序避免资源竞争导致死锁
            sku_q = SKU.objects.filter(id__in=sku_list).order_by('id')
            # 获取被选中的sku
            sku_dict = {sku.id: sku for sku in sku_q}
            for sku_id, sku in sku_dict.items():
                try:
                    # 当前商品要买多少件
                    sku_count = sku_data.get(sku_id)
                    # from time import sleep
                    # sleep(5)

                    '''悲观锁
                    数据库层面执行sql语句，使用行锁锁定该指定行，只有执行事务完释放锁后其他人才可以访问'''
                    stock_num = SKU.objects.filter(id=sku_id, stock__gte=sku_count).update(stock=F('stock') - sku_count,
                                                                                           sales=F('sales') + sku_count)
                    '''乐观锁,使用乐观锁注意事务的隔离级别：一个事务修改的结果要可以被其他事务看到'''
                    # old_stock=sku.stock
                    # new_stock=old_stock - sku_count
                    # new_sales=sku.sales + sku_count
                    # stock_num=SKU.objects.filter(id=sku_id,stock=old_stock).update(stock=new_stock,sales=new_sales)
                    if stock_num == 0:
                        #事务回滚
                        transaction.savepoint_rollback(point)
                        return JsonResponse({'code': 400, 'errmsg': f'商品{sku.name}缺货'})
                    orderinfo.total_count += sku_count
                    orderinfo.total_amount += sku.price * sku_count
                    OrderGoods.objects.create(
                        order=orderinfo,
                        sku=sku,
                        count=sku_count,
                        price=sku.price,
                    )
                except Exception as e:
                    transaction.savepoint_rollback(point)
                    return JsonResponse({'code': 400, 'errmsg': '订单创建失败'})
            orderinfo.save()
            transaction.savepoint_commit(point)
        '''还要清除redis里面选中数据的缓存'''
        client=get_redis_connection('carts')
        pipe=client.pipeline()
        pipe.srem('selected_%s' % user.id, *selected_sku_ids)
        pipe.hdel('carts_%s' % user.id, *selected_sku_ids)
        pipe.execute()
        return JsonResponse({'code': 0, 'errmsg': 'ok','order_id': order_id})
# def can_request(user_id, product_id, limit=5, period=10):
#
#     key = f"rate_limit:{user_id}:{product_id}"
#     client = get_redis_connection('carts')
#     count = client.get(key, 0)
#     if count >= limit:
#         return False
#     client.set(key, count+1, period)
#     return True
def can_request(user_id, product_id, limit=5, period=10):
    """一个用户对于一个商品只能发出5次请求"""
    key = f"rate_limit:{user_id}:{product_id}"
    client = get_redis_connection('carts')

    count = client.incr(key)

    if count == 1:
        client.expire(key, period)

    return count <= limit
class SeckillView(View):
    def post(self, request, product_id):
        user_id = request.user.id
        if not user_id:
            return JsonResponse({"code": 401, "msg": "请登录"})
        r = get_redis_connection('carts')
        # 1. 限流
        if not can_request(user_id, product_id):
            return JsonResponse({"code": 429, "msg": "请求过快"})

        # 2. 检查活动状态
        if not r.exists(f"seckill:status:{product_id}"):
            return JsonResponse({"code": 400, "msg": "活动未开始或已结束"})
        user_key = f"seckill:user:{user_id}:{product_id}"
        if not r.setnx(user_key, 1):
            return JsonResponse({"code": 400, "msg": "不能重复抢购"})

        r.expire(user_key, 3600)
        # 3. Redis预扣库存（原子操作）
        lua_script = """
        local stock = redis.call('GET', KEYS[1])
        if not stock then
            return -1
        end
        if tonumber(stock) <= 0 then
            return -2
        end
        return redis.call('DECR', KEYS[1])
        """
        stock = r.eval(lua_script, 1, f"seckill:stock:{product_id}")
        if stock == -1:
            return JsonResponse({"code": 400, "msg": "库存不存在"})
        if stock == -2:
            return JsonResponse({"code": 400, "msg": "已抢光"})
        # new_stock = r.decr(f"seckill:stock:{product_id}")
        # if new_stock < 0:
        #     # 库存为负时回滚并返回失败
        #     r.incr(f"seckill:stock:{product_id}")
        #     return JsonResponse({"code": 400, "msg": "已抢光"})
        from celery_tasks.seckill.tasks import process_seckill

        # 5. 发送 Celery 任务
        process_seckill.delay(user_id, product_id)

        # 5. 立即返回排队中
        return JsonResponse({"code": 200, "msg": "排队中，请稍后查看结果"})
class SeckillResultView(View):
    def get(self, request, product_id):
        user_id = request.user.id
        r = get_redis_connection('carts')

        result = r.get(f"seckill:result:{user_id}:{product_id}")

        if not result:
            return JsonResponse({"code": 0, "msg": "排队中"})

        if result == b"success":
            return JsonResponse({"code": 1, "msg": "抢购成功"})

        return JsonResponse({"code": -1, "msg": "失败"})
