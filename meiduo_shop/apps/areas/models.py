from django.db import models

# Create your models here.
class Area(models.Model):
    name=models.CharField(max_length=20,verbose_name='名称')
    parent=models.ForeignKey('self',null=True,blank=True,
                             on_delete=models.SET_NULL,
                             verbose_name='上级行政区划',
                             related_name='subs')
    """
    city=Area.objects.filter(parent=13000) 获取省的信息，由于是自关联有一个隐藏字段sub
    city.subs.all()获取该省所有的县
    """
    #related_name是关联的模型的名字
    #默认是关联模型名字小写_set   area_set
    #通过related_name修改默认关联表的名字
    """
    这就是“用默认反向查询名 area_set”的完整含义：
    “父对象.area_set” 等价于 SQL 的 SELECT * FROM tb_areas WHERE parent_id = 父对象.id。
    """
    class Meta:
        db_table='tb_areas'
        verbose_name='省市区'
        verbose_name_plural=verbose_name
    def __str__(self):
        return self.name
