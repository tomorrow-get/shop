'''
celery是基于生产者消费者设计模式
    生产者
        @app.task
        def sms_send_code(mobile,code):
            CCP().send_template_sms(mobile,[code,5],1)
        此外要监听生产者app.autodiscover_tasks(['celery_tasks.sms'])
    消费者
        在终端执行：celery -A proj worker -l INFO
                例如celery -A celery_tasks.main worker -l INFO
                在Windows系统执行
                    celery -A celery_tasks.main worker --loglevel=INFO --pool=eventlet
                    eventlet是一个协程库
                    # eventlet池的工作原理示意图
                        主进程（1个）
                        ├── 协程1：从消息队列获取任务A并执行
                        ├── 协程2：从消息队列获取任务B并执行
                        ├── 协程3：从消息队列获取任务C并执行
                        └── 协程N：...
    中间人（队列）
        broker
    celery把三者结合
        生产者任务把任务放入消息队列
        消费者从消息队列获取任务去执行
        在这一过程中通过celery监听消息队列实现异步执行
'''
import os
#为celery的运行设置django环境
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "meiduo_shop.settings")
from celery import Celery
#创建celery实例
#参数1  main设置脚本路径为meiduo_shop
app = Celery('meiduo_shop',
             broker='redis://127.0.0.1:6379/15',
             backend='redis://127.0.0.1:6379/14'
             )
#设置中间人    消息队列(通过配置文件设置)
# app.config_from_object('celery_tasks.config')
#利用celery检测指定包中的生产者任务
#参数是列表，里面是指定包的路径(生产者任务)
#相当于在celery注册任务，在redis中"_kombu.binding.celery"为任务路由
app.autodiscover_tasks(['celery_tasks.sms','celery_tasks.emails'])
