class Router(object):
    '''配置数据库读写分离'''
    def db_for_read(self, model, **hints):
        return 'slave'
    def db_for_write(self, model, **hints):
        return 'default'
    def allow_relation(self, obj1, obj2, **hints):
        return True
from django.db.utils import ConnectionRouter