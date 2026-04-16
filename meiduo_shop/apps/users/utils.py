from itsdangerous import TimedSerializer
from meiduo_shop import settings
def varify_email(user_id):
    #创建实例,传入密钥
    serializer = TimedSerializer(settings.SECRET_KEY)
    #加密数据
    #data = serializer.dumps(user_id)加密为一个字符串
    #data = serializer.dumps(‘user_id:’user_id)手动加密一个字典dic{user_id:data}
    data = serializer.dumps(user_id)
    return data
def check_email(token):
    serializer = TimedSerializer(settings.SECRET_KEY)
    try:
        data = serializer.loads(token)
    except Exception as e:
        return None
    return data