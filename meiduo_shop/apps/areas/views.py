from django.http import JsonResponse
from django.shortcuts import render
from django.views import View

from apps.areas.models import Area
from django.core.cache import cache

# Create your views here.
class AddressView(View):
    """获取省数据"""
    def get(self, request):
        #利用djando的cache缓存
        province=cache.get('province')
        if province is None:
            provinces=Area.objects.filter(parent=None)
            province=[{'id':i.id,'name':i.name} for i in provinces]
            cache.set('province',province,24*3600)
        return JsonResponse({'code':0,'errmsg':'ok','province_list':province})
class SubaddressView(View):
    """获取县数据"""
    def get(self, request,id):
        country=cache.get('city:%s'%id)
        if country is None:
            #由省id查询对应县id
            data=Area.objects.get(id=id)
            countries=data.subs.all()
            country=[{'id':i.id,'name':i.name} for i in countries]
            cache.set('city:%s'%id,country,24*3600)
        return JsonResponse({'code':0,'errmsg':'ok','sub_data':{'subs':country}})