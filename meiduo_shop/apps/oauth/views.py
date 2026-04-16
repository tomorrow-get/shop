import json
import re
from http.client import responses

import redis
from django.contrib.auth import login
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from QQLoginTool.QQtool import OAuthQQ
from django_redis import get_redis_connection

from apps.carts.utils import merge_cookie_to_redis
from apps.oauth.models import OAuthQQUser
from apps.users.models import User
from meiduo_shop import settings
"""
第三方登录，注册成为开发者，为自己网站获取一个登录qq的客户端id和密钥,申请用户同意后跳转的url
第三方登录流程
    1.添加qq图标（点击后跳转一个网址）
    2.跳转的网址要携带qq的客户端id。qq的客户端密钥。用户同意授权后跳转的链接。state
    3.成功后会获取一个用户的code,把code换成token，再把token换成用户的openid
    4.将用户信息与得到用户的openid绑定
"""
# Create your views here.
class QQOauthView(View):
    def get(self, request):
        # client_id=None, 开发者为网站申请的客户端id
        # client_secret=None, 开发者为网站申请的客户端的私钥
        # redirect_uri=None, 用户同意后跳转的url地址（该地址会携带返回的code）
        # state=None 暂时不考虑，用于crsf认证
        #1.生成OAuthQQ实例对象
        qq=OAuthQQ(client_id=settings.QQ_CLIENT_ID,
                      client_secret=settings.QQ_CLIENT_SECRET,
                      redirect_uri=settings.QQ_REDIRECT_URI,
                      state='xxxx')
        #2.获取qq跳转url,即用户点击qq按钮后跳转到哪里
        qq_login=qq.get_qq_url()
        return JsonResponse({'code':0,'errmsg':'ok','login_url':qq_login})
class QQLoginView(View):
    def get(self, request):
        code = request.GET.get('code')
        if code is None:
            return JsonResponse({'code':400,'errmsg':'参数缺失'})
        qq=OAuthQQ(client_id=settings.QQ_CLIENT_ID,
                      client_secret=settings.QQ_CLIENT_SECRET,
                      redirect_uri=settings.QQ_REDIRECT_URI,
                      state='xxxx')
        qq_token=qq.get_access_token(code)
        openid=qq.get_open_id(qq_token)
        try:
            qq_user=OAuthQQUser.objects.get(openid=openid)
            #get方法若为空会发生异常
        except OAuthQQUser.DoesNotExist:
            #用户不存在，是首次登录，要绑定
            response=JsonResponse({'code':'400','access_token':openid})
        else:
            #没有异常
            response=JsonResponse({'code':0,'errmsg':'ok'})
            response.set_cookie('username',qq_user.user.username)
        #最终都会执行
        return response
    def post(self, request):
        data=json.loads(request.body.decode())
        mobile=data.get('mobile')
        password=data.get('password')
        sms_code=data.get('sms_code')
        openid=data.get('access_token')
        if not all([mobile,password,sms_code,openid]):
            return JsonResponse({'code':400,'errmsg':'参数不全'})
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return JsonResponse({'code':400,'errmsg':'手机号格式错误'})
        if len(password) < 8 or len(password) > 20:
            return JsonResponse({'code':400,'errmsg':'密码格式错误'})
        redis_cli=get_redis_connection('code')
        sms_code_test=redis_cli.get(mobile)
        if sms_code_test is None:
            return JsonResponse({'code': 400, 'errmsg': '短信验证码过期'})
        if sms_code_test.decode()!=sms_code:
            return JsonResponse({'code': 400, 'errmsg': '短信验证码错误'})
        try:
            user = User.objects.get(mobile=mobile)
        except User.DoesNotExist:
            user=User.objects.create_user(username=mobile,mobile=mobile,password=password,email=None)
        else:
            if not user.check_password(password):
                return JsonResponse({'code': 400, 'errmsg': '用户名或密码错误'})
        #外键看似关联整个User对象，实际只是关联User的id，同时可可以通过user查看User表中的数据
        OAuthQQUser.objects.create(user=user,openid=openid)

        login(request,user)
        merge_cookie_to_redis(request)
        response=JsonResponse({'code':0,'errmsg':'ok'})
        response.set_cookie('username',user.username)
        response.delete_cookie('carts')
        return response