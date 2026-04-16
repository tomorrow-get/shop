from django.db import models

from apps.users.models import User
from utils.models import BaseModel


# Create your models here.
class OAuthQQUser(BaseModel):
    user=models.ForeignKey(User,on_delete=models.CASCADE,verbose_name='用户')
    openid=models.CharField(max_length=64,verbose_name='openid',db_index=True)
    class Meta:
        db_table='db_oauth_qq'
        verbose_name='qq用户登录数据'
        verbose_name_plural=verbose_name