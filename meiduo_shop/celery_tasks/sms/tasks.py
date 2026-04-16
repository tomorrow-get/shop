from celery_tasks.main import app
from libs.yuntongxun.sms import CCP

#生产者任务
#1.该生产者函数必须被celery的task装饰器装饰
#2.需要celery自动检测该软件包中的任务
@app.task
def sms_send_code(mobile,sms_code):
    CCP().send_template_sms(mobile,[sms_code,5],1)