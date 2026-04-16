from django.http import JsonResponse
from apps.goods.models import SKU
from haystack import indexes
"""
1.需要在对应模型中子应用下创建search_indexes.py 方便haystack来检索数据
2.索引类必须继承自indexes.SearchIndex,indexes.Indexable
3.必须定义字段document=True，当用户输入关键词搜索时，haystack 默认就在这个字段中查找
4.use_template=True 告诉 haystack：不要直接从模型取单个字段，而是渲染一个模板文件来生成搜索文本。
    为什么需要这个？
    通常一个模型有多个字段需要被搜索（如商品名、副标题、描述、分类名），
    但你希望用户搜索任意一个关键词都能匹配到这个商品。
"""
"""
完整索引构建流程
# 当你运行 python manage.py rebuild_index 时：

1. 遍历所有 SKU 对象（index_queryset 返回的查询集）
2. 对每个 SKU 实例：
   a. 加载模板：templates/search/indexes/goods/sku_text.txt
   b. 渲染模板 → 得到 "iPhone 15 手机 苹果 智能手机..."
   c. 将这段文本存入 Elasticsearch/Solr/Whoosh 的 text 字段
3. 完成索引建立
"""
class SKUIndex(indexes.SearchIndex,indexes.Indexable):
    text = indexes.CharField(document=True,use_template=True)
    def get_model(self):
        #建立索引的模型类
        return SKU
    def index_queryset(self, using=None):
        #返回要建立索引的数据查询结果集
        return self.get_model().objects.all()
