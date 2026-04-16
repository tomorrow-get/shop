import json
import re
from http.client import responses
from json import loads

import redis
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.db import transaction
from django.dispatch import receiver
from django.http import JsonResponse
from django.template.defaultfilters import title

from django.views import View
from django_redis import get_redis_connection

from apps.carts.utils import merge_cookie_to_redis
from apps.goods.models import SKU
from apps.users import utils
from apps.users.models import User, Address
from meiduo_shop.settings import EMAIL_HOST_USER


# Create your views here.
class UsernamecountView(View):
    def get(self, request,username):
        #利用类视图添加检测用户名是否重名逻辑判断
        count = User.objects.filter(username=username).count()
        return  JsonResponse({'code':0,'count':count,'errmsg':'ok'})
class MobilecountView(View):
    def get(self, request, mobile):
        count = User.objects.filter(mobile=mobile).count()
        return JsonResponse({'code':0,'count':count,'errmsg':'ok'})
class RegisterView(View):
    def post(self,request):
        try:
            with transaction.atomic():#保证事务一致性
                body_dict = json.loads(request.body.decode())
                username = body_dict.get('username')
                password = body_dict.get('password')
                password2 = body_dict.get('password2')
                mobile = body_dict.get('mobile')
                allow = body_dict.get('allow')
                sms_code=body_dict.get('sms_code')
                # 检测设否有空值
                if not all([username, password, password2, mobile]):
                    return JsonResponse({'code': 400, 'errmsg': '缺少参数'})
                if not allow:
                    return JsonResponse({'code': 400, 'errmsg': '请勾选同意协议'})
                if password != password2:
                    return JsonResponse({'code': 400, 'errmsg': '前后密码输入不一致'})
                if not re.match(r'^1[3-9]\d{9}$', mobile):
                    return JsonResponse({'code': 400, 'errmsg': '手机号输入格式错误'})
                if not re.match(r'^[0-9A-Za-z_-]{5,20}$', username):
                    return JsonResponse({'code': 400, 'errmsg': '用户名输入格式错误'})
                if not re.match(r'^.{8,20}$', password):
                    return JsonResponse({'code': 400, 'errmsg': '密码输入格式错误'})
                # User.objects.create_user(username=username,password=password,mobile=mobile)
                # 连接redis验证短信验证码是否正确
                redis_cli = get_redis_connection('code')
                sms_data = redis_cli.get(mobile)
                if sms_data is None:
                    return JsonResponse({'code': 400, 'errmsg': '短信验证码过期'})
                if sms_code != sms_data.decode():
                    return JsonResponse({'code': 400, 'errmsg': '短信验证码输入错误'})
                # 上述代码插入数据时密码自动加密
                user=User.objects._create_user(username=username, password=password, mobile=mobile, email=None)
                #配置session状态保持，向redis数据库写入信息
                login(request,user)
                return JsonResponse({'code': 0, 'errmsg': 'ok'})
        except Exception as e:
            return JsonResponse({'code': 400, 'errmsg': str(e)})
class LoginView(View):
    def post(self,request):
        #1.获取数据
        data = json.loads(request.body.decode())
        username = data.get('username')
        password = data.get('password')
        remembered = data.get('remembered')

        #2.检查数据
        if not all([username, password]):
            return JsonResponse({'code':400,'errmsg':'参数不全'})
        if re.match(r'^1[3-9]\d{9}$', username):
            #USERNAME_FIELD字段是查询数据库时所用
            #实现用户多信息登录
            User.USERNAME_FIELD='mobile'#手机号登录
        #3.校验参数,利用django提供的校验方法
        # user = User.objects.get(username=username, password=password)注意密码要加密
        from django.contrib.auth import authenticate, login
        user = authenticate(username=username, password=password)
        if user is None:
            return JsonResponse({'code': 400, 'errmsg': '用户名或密码错误'})
        #4.状态保持
        login(request,user)
        #5.是否保持登录状态
        if remembered:
            request.session.set_expiry(None)
        else:
            #浏览器关闭时session过期
            request.session.set_expiry(0)
        #4.1合并购物车
        merge_cookie_to_redis(request)
        response= JsonResponse({'code': 0, 'errmsg': 'ok'})
        response.set_cookie('username', user.username)
        response.delete_cookie('carts')
        return response
from django.contrib.auth import logout
class LogoutView(View):
    def delete(self,request):
        #删除session信息
        logout(request)
        response= JsonResponse({'code': 0, 'errmsg': 'ok'})
        #删除cookie信息
        response.delete_cookie('username')
        return response
from utils.views import LoginRequiredJsonMixin
class CenterView(LoginRequiredJsonMixin,View):
    def get(self, request):
        #request.user就是已经登录的用户的信息（登录用户信息可以用login(request,user)保存
        #request.user内容源于中间件
        #系统会进行判断，若我们已经登录request.user会返回登录用户的对象
        #若用户没有登录request.user返回AnonymousUser()用户匿名对象
        info_data={
            'username':request.user.username,
            'mobile':request.user.mobile,
            'email':request.user.email,
            'email_active':request.user.email_active,
        }
        return JsonResponse({'code': 0, 'errmsg': 'ok','info_data':info_data})
# class CenterView(View):
#     def get(self, request):
#         user=request.COOKIES.get('username')
#         if not user:
#             return JsonResponse({'code': 0, 'errmsg': '用户未登录'})
#         info_data={
#             'username':request.user.username,
#             'mobile':request.user.mobile,
#             'email':request.user.email,
#             'email_active':request.user.email_active,
#         }
#         return JsonResponse({'code': 0, 'errmsg': 'ok','info_data':info_data})
class EmailView(LoginRequiredJsonMixin,View):
    def put(self, request):
        data = json.loads(request.body.decode())
        email = data.get('email')
        if not email:
            return JsonResponse({'code': 400, 'errmsg': '参数缺失'})
        if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return JsonResponse({'code': 0, 'errmsg': '参数格式错误'})
        #保存用户邮件信息
        user=request.user
        user.email=email
        user.save()
        #加密的数据
        token = utils.varify_email(user.id)
        verify_url="http:www.meiduo.site:8080/success_verify_email.html"
        html_message = f"点击下面的激活按钮激活邮箱<a href='{verify_url}?token={token}'>激活</a>"
        # 异步发送验证邮件
        from celery_tasks.emails import tasks
        #定义参数
        subject = '每多商城激活邮件'
        message = ''
        from_email = EMAIL_HOST_USER
        recipient_list = ['15612383794@163.com']
        html_message = html_message
        #celery可序列化对象为json数据，传入的参数必须可序列化，不能是对象
        tasks.send_email.delay(subject,message,from_email,recipient_list,html_message)
        return JsonResponse({'code': 0, 'errmsg': 'ok'})
# class VerifyEmailView(View):
#     def put(self,request):
#         data = request.GET#返回结果是django封装的字典
#         token=data.get("token")
#         if token is None:
#             return JsonResponse({'code':400,'errmsg':'参数缺失'})
#         result=utils.check_email(token)
#         if result is None:
#             return JsonResponse({'code': 400, 'errmsg': '参数错误'})
#         user=User.objects.get(id=result)
#         user.email_active=True#激活邮件
#         user.save()
#         return JsonResponse({'code': 0, 'errmsg': 'ok'})
class VerifyEmailView(View):
    def put(self,request):
        data = request.GET#返回结果是django封装的字典
        token=data.get("token")
        if token is None:
            return JsonResponse({'code':400,'errmsg':'参数缺失'})
        result=utils.check_email(token)
        if result is None:
            return JsonResponse({'code': 400, 'errmsg': '参数错误'})
        if request.user.id==result:
            request.user.email_active=True
            request.user.save()
            return JsonResponse({'code': 0, 'errmsg': 'ok'})
        return JsonResponse({'code': 400, 'errmsg': '错误'})
class AddressCreateView(LoginRequiredJsonMixin,View):
    def post(self,request):
        #request.body获得的只是二进制字节流
        if request.user.address.count() >20:
            return JsonResponse({'code': 400, 'errmsg': '地址最多保存20个'})
        data = json.loads(request.body.decode())
        receiver=data.get('receiver')
        province_id=data.get('province_id')
        city_id=data.get('city_id')
        district_id=data.get('district_id')
        place=data.get('place')
        mobile=data.get('mobile')
        email=data.get('email')
        tel=data.get('tel')
        user=request.user
        #验证必要参数
        if not all([receiver,province_id,city_id,district_id,place.mobile]):
            return JsonResponse({'code':400,'errmsg':'缺少必要参数'})
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return JsonResponse({'code': 400, 'errmsg': '手机号错误'})
        if tel:
            if not re.match(r'^0\d{2,3}-?\d{7,8}$', tel):
                return JsonResponse({'code': 400, 'errmsg': '固定电话错误'})
        if email:
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
                return JsonResponse({'code': 400, 'errmsg': '邮箱错误'})
        #数据入库
        new_address=Address.objects.create(
            user=user,
            receiver=receiver,
            province_id=province_id,
            city_id=city_id,
            district_id=district_id,
            place=place,
            tel=tel,
            email=email,
            mobile=mobile,
            title=receiver
        )
        address={
            'id': new_address.id,
            'title': new_address.title,
            'receiver': new_address.receiver,
            'province': new_address.province.name,
            'city': new_address.city.name,
            'district': new_address.district.name,
            'place': new_address.place,
            'tel': new_address.tel,
            'email': new_address.email,
            'mobile': new_address.mobile,
        }
        return JsonResponse({'code': 200, 'errmsg': 'ok', 'address':address})
class AddressView(LoginRequiredJsonMixin,View):
    def get(self,request):
        #获取用户添加的地址
        user=request.user
        address=Address.objects.filter(user=user,is_deleted=False)
        addresses=[{'id': new_address.id,
            'title': new_address.title,
            'receiver': new_address.receiver,
            'province': new_address.province.name,
            'city': new_address.city.name,
            'district': new_address.district.name,
            'place': new_address.place,
            'tel': new_address.tel,
            'email': new_address.email,
            'mobile': new_address.mobile} for new_address in address if new_address is not None]
        return JsonResponse({'code': 200, 'errmsg': 'ok', 'addresses':addresses,'default_address_id':request.user.default_address_id
        })
class AddressUpdateView(LoginRequiredJsonMixin,View):
    def put(self,request,address_id):
        """编辑后更新地址"""
        try:
            address=Address.objects.get(id=address_id,is_deleted=False,user=request.user)
        except Exception as e:
            return JsonResponse({'code': 400, 'errmsg': '编辑的地址不存在'})
        data=json.loads(request.body.decode())
        update_fields = {k: v for k, v in data.items()
                         if k in {'receiver', 'province_id', 'city_id', 'district_id',
                                  'place', 'mobile', 'email', 'tel'} and v}
        for i,j in update_fields.items():
            setattr(address, i, j)
        address.save()
        """缺少逻辑"""
        # 构建返回的地址数据
        address_data = {
            'id': address.id,
            'title': address.title,
            'receiver': address.receiver,
            'province':  address.province.name,
            'city':  address.city.name,
            'district':address.district.name,
            'place': address.place,
            'mobile': address.mobile,
            'tel': address.tel,
            'email': address.email,
            'is_deleted': address.is_deleted,
        }
        return JsonResponse({'code': 200, 'errmsg': 'ok','address':address_data})
    def delete(self,request,address_id):
        """逻辑删除地址"""
        try:
            address=Address.objects.get(id=address_id,is_deleted=False,user=request.user)
            #逻辑删除
            address.is_deleted=True
            #物理删除address.delete()
            address.save()
            return JsonResponse({'code': 0, 'errmsg': 'ok'})
        except Exception as e:
            return JsonResponse({'code': 400, 'errmsg': '地址不存在'})
class AddressDefaultView(LoginRequiredJsonMixin,View):
    """设置默认地址"""
    def put(self,request,address_id):
        #address_id是默认地址
        user=request.user
        address=Address.objects.get(id=address_id,is_deleted=False,user=request.user)
        user.default_address=address
        user.save()
        return JsonResponse({'code': 0, 'errmsg': 'ok','default_address_id': address.id})
class AddressTitleView(LoginRequiredJsonMixin,View):
    def put(self,request,address_id):
        """保存修改后的标题"""
        #利用filter返回的是列表，利用get返回单个值
        address=Address.objects.filter(id=address_id,is_deleted=False,user=request.user).first()
        data=json.loads(request.body.decode())
        title=data.get('title')
        if title is None:
            return JsonResponse({'code': 400, 'errmsg': '标题不能为空'})
        address.title=title
        address.save()
        return JsonResponse({'code': 200, 'errmsg': 'ok'})
from datetime import date
class UserHistoryView(LoginRequiredJsonMixin,View):
    def post(self,request):
        user=request.user
        try:
            sku_id=json.loads(request.body.decode()).get('sku_id')
            sku=SKU.objects.get(id=sku_id)
        except Exception as e:
            return JsonResponse({'code':400,'errmsg':'请求错误'})
        redis_cli=get_redis_connection('history')
        history_key=f"history_{user.id}"
        # 使用管道批量操作,核心目的是减少网络往返延迟,允许你将多个命令一次性发送到服务器，而不必等待每个命令的单独响应。
        pipe=redis_cli.pipeline()
        import time
        current_timestamp = int(time.time() * 1000)
        pipe.zadd(history_key, {sku_id: current_timestamp})
        #移除有序集合，键 start end
        pipe.zremrangebyrank(history_key, 0, -6)
        # 4. 设置过期时间（可选，比如30天）
        pipe.expire(history_key, 60 * 60 * 24 * 30)
        # 执行所有命令
        pipe.execute()
        return JsonResponse({'code': 0, 'errmsg': 'ok'})
    def get(self,request):
        user=request.user
        redis_cli=get_redis_connection('history')
        history_key=f"history_{user.id}"
        data=redis_cli.zrange(history_key, 0, -1)
        data.reverse()
        history=[]
        for sku_id in data:
            try:
                sku = SKU.objects.get(id=sku_id)
                history.append({
                    'id': sku.id,
                    'name': sku.name,
                    'default_image_url': sku.default_image.url,
                    'price': sku.price,
                })
            except SKU.DoesNotExist:
                continue
        return JsonResponse({'code': 0, 'errmsg': 'ok', 'skus':history})