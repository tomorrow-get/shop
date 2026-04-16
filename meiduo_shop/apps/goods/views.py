from django.http import JsonResponse
from django.shortcuts import render

from django.views import View
from django_redis import get_redis_connection
from unicodedata import category

from apps.goods.models import GoodsCategory, SKU, GoodsVisitCount


# Create your views here.
class IndexView(View):
    """查询商品列表"""
    def get(self, request,category):
        #获取参数
        #排序字段
        ordering=request.GET.get('ordering')
        #每页大小
        page_size=request.GET.get('page_size')
        #要第几页
        page_num = request.GET.get('page')
        #获取分类id
        try:
            category=GoodsCategory.objects.get(id=category)
        except GoodsCategory.DoesNotExist:
            return JsonResponse({'code':400,'errmsg':'分类不存在或已被删除'})
        #获取面包屑信息
        from utils.goods import get_breadcrumb
        breadcrumb=get_breadcrumb(category)
        #查询对应分类id对应的具体商品信息
        goods=SKU.objects.filter(category=category,is_launched=True).order_by(ordering)
        #############分页################
        from django.core.paginator import Paginator
        """Paginator参数
        object_list页面所含的数据
         per_page每页大小是多少
        """
        #构造分页
        paginator = Paginator(goods,page_size)
        #获取分页数据(获取的是对象列表）要把对象转化为列表数据利用：object_list
        pages = paginator.page(page_num)
        page_list = [
            {
                'id': page.id,
                'name': page.name,
                'price': page.price,
                'default_image_url': page.default_image.url,
            }
            for page in pages.object_list
        ]
        #获取总页码
        total_page=paginator.num_pages
        return JsonResponse({'code':0,'errmsg':'ok','breadcrumb':breadcrumb,'list':page_list,'count':total_page})
class HotView(View):
    def get(self, request,cat_id):
        try:
            category=GoodsCategory.objects.get(id=cat_id)
        except GoodsCategory.DoesNotExist:
            return JsonResponse({'code':400,'errmsg':'分类不存在或已被删除'})
        goods=(SKU.objects.filter(category=category,is_launched=True).order_by('sales'))[:3]
        page_list = [
            {
                'id': page.id,
                'name': page.name,
                'price': page.price,
                'default_image_url': page.default_image.url,
            }
            for page in goods
        ]
        return JsonResponse({'code':0,'errmsg':'ok','hot_skus':page_list})
# from haystack.views import SearchView
# #数据是借助于haystack对接Elasticsearch，不能直接用View
# class SKUSearchview(SearchView):
#     def create_response(self):
#         #获取查询结果
#         context=self.get_context()
#         sku_list=[]
#         for sku in context['page'].object_list:
#             sku_list.append({
#                 'id': sku.object.id,
#                 'name': sku.object.name,
#                 'price': sku.object.price,
#                 'default_image_url': sku.object.default_image.url,
#                 'searchkey':context.get('query'),
#                 'page_size':context['page'].paginator.num_pages,
#                 'count':context['page'].paginator.count,
#             })
#         return JsonResponse(sku_list, safe=False)

class DetailView(View):
    def get(self, request,sku_id):
        try:
            sku=SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            pass
        from utils.goods import get_breadcrumb, get_categories, get_goods_specs
        #获取分类数据
        categories= get_categories()
        #获取面包屑
        breadcrumb=get_breadcrumb(sku.category)
        #获取规格数据
        good_specs=get_goods_specs(sku)
        context={
            'sku':sku,
            'breadcrumb':breadcrumb,
            'categories':categories,
            'good_specs':good_specs,
        }
        return render(request,'detail.html',{'context':context})
from datetime import date
from django.db.models import F
from django.db import IntegrityError, transaction
from django.db.models import F
from django.utils.timezone import now

class DetailVisitView(View):
    def post(self, request, category_id):
        '''方法1：利用MySQL实现'''
        try:
            category = GoodsCategory.objects.get(id=category_id)
        except GoodsCategory.DoesNotExist:
            return JsonResponse({'code': 400, 'errmsg': '非法分类'})

        today = now().date()
        redis_cli=get_redis_connection('goods_count')
        key=f"{today}:{category.id}"
        if redis_cli.setnx(key, 1):
            #设置成功
            return JsonResponse({'code': 0, 'errmsg': 'ok'})
        else:
            #键已经存在
            redis_cli.incr(key)
            return JsonResponse({'code': 0, 'errmsg': 'ok'})
        # # 先尝试更新（原子操作）
        # updated = GoodsVisitCount.objects.filter(
        #     category=category, date=today
        # ).update(count=F('count') + 1)
        #
        # if updated == 0:
        #     # 记录不存在，尝试创建
        #     try:
        #         GoodsVisitCount.objects.create(
        #             category=category, date=today, count=1
        #         )
        #     except IntegrityError:
        #         # 并发创建冲突，其他请求已经插入记录，再次更新
        #         GoodsVisitCount.objects.filter(
        #             category=category, date=today
        #         ).update(count=F('count') + 1)
        '''方法2：利用redis+定时任务'''

        return JsonResponse({'code': 0, 'errmsg': 'ok'})
'''或者利用悲观锁
with transaction.atomic():
    obj, created = GoodsVisitCount.objects.select_for_update().get_or_create(
        category=category, date=today, defaults={'count': 1}
    )
    if not created:
        obj.count = F('count') + 1
        obj.save(update_fields=['count'])
'''
