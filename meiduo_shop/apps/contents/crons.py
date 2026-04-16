'''首页页面的静态化,每次访问首页都要从数据库查数据渲染到首页，严重影响用户体验
    应该提前渲染好页面，只返回一个渲染好的静态页面，优化用户体验
    之后首页有什么更新可以直接在服务器端运行函数重新渲染页面
'''
import os
import time
from collections import OrderedDict

from apps.contents.models import ContentCategory
from apps.goods.models import GoodsChannel
from meiduo_shop import settings


def generic_get_index():
    print("-----------%s---------"%time.ctime())
    """首页广告展示
    1.获取商品数据categories
    2.获取广告数据contents
    """
    # 1.定义一个有序字典
    categories = OrderedDict()
    # 对 GoodsChannel 进行 group_id 和 sequence 排序, 获取排序后的结果:
    goods = GoodsChannel.objects.order_by('group_id', 'sequence')
    # 遍历排序后的结果: 得到所有的一级菜单( 即,频道 )
    for good in goods:
        # 从频道中得到当前的 组id
        group_id = good.group_id
        # 判断: 如果当前 组id 不在我们的有序字典中:
        if group_id not in categories:
            # 把 组id 添加到 有序字典中
            categories[group_id] = {'channels': [], 'sub_cats': []}
        # 获取当前频道的分类名称(一级广告)
        cat1 = good.category
        # 添加一级组信息信息
        categories[group_id]['channels'].append({'id': cat1.id, 'name': cat1.name, 'url': good.url})
        for cat2 in cat1.subs.all():
            # 创建一个新的列表:
            cat2.sub_cats = []
            for cat3 in cat2.subs.all():
                cat2.sub_cats.append(cat3)
            categories[group_id]['sub_cats'].append(cat2)
    contents = {}
    content_categories = ContentCategory.objects.all()
    for category in content_categories:
        '''
        category.content_set：
        这是Django的反向查询
        假设有一个 Content 模型，它有一个外键指向 ContentCategory：
        '''
        contents[category.id] = category.content_set.filter(status=True).order_by('sequence')
    context = {
        'categories': categories,
        'contents': contents
    }
    from django.template import  loader
    #获取渲染的页面（加载渲染的模板）
    template = loader.get_template('index.html')
    #向模板传递数据
    index_html=template.render(context)
    #把渲染好的HTML传递给指定位置
    file_path=os.path.join(os.path.dirname(settings.BASE_DIR),'front_end_pc/index.html')
    with open(file_path,'w',encoding='utf-8') as f:
        f.write(index_html)
