import os
from collections import OrderedDict
from django.shortcuts import render
from django.views import View
from kombu.abstract import Object

from apps.contents.models import ContentCategory
from apps.goods.models import GoodsChannel
from apps.users.urls import urlpatterns
from meiduo_shop import settings


# Create your views here.
class IndexView(View):
    """首页广告"""
    def get(self, request):
        """首页广告展示
        1.获取商品数据categories
        2.获取广告数据contents
        """
        #1.定义一个有序字典
        categories=OrderedDict()
        # 对 GoodsChannel 进行 group_id 和 sequence 排序, 获取排序后的结果:
        goods=GoodsChannel.objects.order_by('group_id','sequence')
        # 遍历排序后的结果: 得到所有的一级菜单( 即,频道 )
        for good in goods:
            # 从频道中得到当前的 组id
            group_id=good.group_id
            # 判断: 如果当前 组id 不在我们的有序字典中:
            if group_id not in categories:
                #把 组id 添加到 有序字典中
                categories[group_id]={'channels':[],'sub_cats': []}
            # 获取当前频道的分类名称(一级广告)
            cat1 = good.category
            #添加一级组信息信息
            categories[group_id]['channels'].append({'id':cat1.id,'name':cat1.name,'url':good.url})
            for cat2 in cat1.subs.all():
                # 创建一个新的列表:
                cat2.sub_cats =[]
                for cat3 in cat2.subs.all():
                    cat2.sub_cats.append(cat3)
                categories[group_id]['sub_cats'].append(cat2)
        contents={}
        content_categories=ContentCategory.objects.all()
        for category in content_categories:
            '''
            category.content_set：
            这是Django的反向查询
            假设有一个 Content 模型，它有一个外键指向 ContentCategory：
            '''
            contents[category.id]=category.content_set.filter(status=True).order_by('sequence')
        context = {
            'categories': categories,
            'contents': contents
        }
        return render(request,'index.html',context)
