"""编写自定义存储系统
1.自定义文件存储类必须继承自Storage(from django.core.files.storage import Storage)
2.自定义文件存储类必须可以无参数实现实例化
3.自定义文件存储类必须实现_open和_save方法，以及适用于我存储系统的其他方法
"""
from django.core.files.storage import Storage

from meiduo_shop import settings


class MyStorage(Storage):
    def _open(self, name, mode='rb'):
        pass
    def _save(self, name, content):
        pass
    def url(self, name):
        return settings.MEDIA_URL + name