from django.http import HttpResponse, JsonResponse

from django.views import View
from django_redis import get_redis_connection


# Create your views here.
class Imageview(View):
    def get(self, request,uuid):
        import libs.captcha.captcha
        text,image=libs.captcha.captcha.captcha.generate_captcha()
        print(text)
        #连接redis
        redis_cli=get_redis_connection('code')
        #插入数据
        redis_cli.setex(uuid,60,text)
        #图片是二进制数据，可直接返回HTTP。content_type用于声明返回响应体类型大类/小类
        return HttpResponse(image,content_type='image/jpeg')
class Smsview(View):
    def get(self, request,mobile):
        image_code=request.GET.get('image_code')
        image_code_id=request.GET.get('image_code_id')
        #验证参数
        if not all([image_code,image_code_id]):
            return  JsonResponse({'code':400,'errmsg':'参数缺失'})
        try:
            # 连接redis
            redis_cli = get_redis_connection('code')
            #利用管道避免多次连接断开redis带来的性能损失
            pipeline=redis_cli.pipeline()
            data=redis_cli.get(image_code_id)
            if not data:
                return JsonResponse({'code':400,'errmsg':'图片验证码过期'})
            if data.decode()==image_code:
                #提取状态标记位
                send_flag_mobile=redis_cli.get('send_flag_%s'%mobile)
                if send_flag_mobile:
                    return JsonResponse({'code':400,'errmsg':'错误：请求过于频繁'})
                from random import randint
                sms_code = '%04d'%randint(1000, 9999)
                pipeline.setex(mobile,300,sms_code)
                #添加状态标记位避免频繁发送
                pipeline.setex('send_flag_%s'%mobile,60,1)
                #执行管道--运行这一步才向redis插入数据，管道类似于一个缓存区
                pipeline.execute()
                # from libs.yuntongxun.sms import CCP
                # CCP().send_template_sms(mobile,[sms_code,5],1)
                #利用celery实现异步发送短信
                from celery_tasks.sms.tasks import sms_send_code
                #把发送短信的任务放入消息队列,利用delay()放入消息队列，立即返回，不阻塞该函数
                # sms_send_code中的参数就是delay的参数
                sms_send_code.delay(mobile,sms_code)
                return JsonResponse({'code':0,'errmsg':'ok'})
            else:
                return JsonResponse({'code':400,'errmsg':'图片验证码错误'})
        except Exception as e:
            return JsonResponse({'code':400,'errmsg':e})
