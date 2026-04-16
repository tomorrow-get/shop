from django.contrib.auth.models import AbstractUser
from django.db import models

from apps import areas
# utils/models.py
from django.db import models

class BaseModel(models.Model):
    """公共字段基类，不会生成表"""
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        abstract = True   # 关键：声明抽象，不会真的建表

# Create your models here.
class User(AbstractUser):
    mobile=models.CharField(max_length=11,unique=True)
    email_active=models.BooleanField(default=False,verbose_name='邮箱验证状态')
    default_address=models.ForeignKey('Address',null=True,blank=True,related_name='users',on_delete=models.SET_NULL,verbose_name='默认地址')
    class Meta:
        db_table='tb_users'
        verbose_name='用户管理'
        verbose_name_plural=verbose_name
    def __str__(self):
        return self.username
class Address(BaseModel):
    user=models.ForeignKey(to=User,on_delete=models.CASCADE,verbose_name='用户',related_name='address')
    title=models.CharField(max_length=20,verbose_name='地址名称')
    receiver=models.CharField(max_length=20,verbose_name='收件人')
    province=models.ForeignKey('areas.Area',on_delete=models.PROTECT,related_name='province_address')
    city=models.ForeignKey('areas.Area',on_delete=models.PROTECT,related_name='city_address')
    district=models.ForeignKey('areas.Area',on_delete=models.PROTECT,related_name='district_address')
    place=models.CharField(max_length=50,verbose_name='地址')
    mobile=models.CharField(max_length=11,verbose_name='手机号')
    tel=models.CharField(max_length=20,null=True,blank=True,default='',verbose_name='固定电话')
    email=models.CharField(max_length=30,null=True,blank=True,default='',verbose_name='电子邮件')
    is_deleted=models.BooleanField(default=False,verbose_name='逻辑删除')
    class Meta:
        db_table='tb_address'
        verbose_name='用户地址'
        verbose_name_plural=verbose_name
        ordering=['-update_time']
