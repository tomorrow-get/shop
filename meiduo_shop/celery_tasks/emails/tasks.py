from django.core.mail import send_mail
        #subject,邮件主题
        # message, 邮件具体内容
        # from_email,邮件来自哪里
        # recipient_list,邮件发送给谁
from celery_tasks.main import app
from apps.users import utils

@app.task
def send_email(subject,message,from_email,recipient_list,html_message):
    send_mail(subject=subject,
              message=message,
              from_email=from_email,
              recipient_list=recipient_list,
              html_message=html_message)