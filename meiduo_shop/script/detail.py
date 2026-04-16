#!/usr/bin/env python
import sys
#定位到上级目录
sys.path.insert(0,'../')
#告诉django的配置文件在哪里
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "meiduo_shop.settings")
import django
django.setup()
from apps.goods.models import SKU
from meiduo_shop import settings

#由运维人员操控生成
def get_detail_html(sku_id):
    try:
        sku = SKU.objects.get(id=sku_id)
    except SKU.DoesNotExist:
        pass
    from utils.goods import get_breadcrumb, get_categories, get_goods_specs
    # 获取分类数据
    categories = get_categories()
    # 获取面包屑
    breadcrumb = get_breadcrumb(sku.category)
    # 获取规格数据
    good_specs = get_goods_specs(sku)
    context = {
        'sku': sku,
        'breadcrumb': breadcrumb,
        'categories': categories,
        'good_specs': good_specs,
    }
    from django.template import loader
    template = loader.get_template('detail.html')
    detail_html = template.render(context)
    file_path=os.path.join(os.path.dirname(settings.BASE_DIR),f'front_end_pc/goods/{sku_id}.html')
    with open(file_path,'w',encoding='utf-8') as f:
        f.write(detail_html)
#文件为脚本文件
skus=SKU.objects.all()
for sku in skus:
    get_detail_html(sku.id)