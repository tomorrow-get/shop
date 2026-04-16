



from datetime import datetime
from django.db import transaction
from django.db.models import F
from django_redis import get_redis_connection
from apps.goods.models import GoodsVisitCount



def merge_redis_goods_count():
    """
    将 Redis 中的商品分类访问量合并到数据库，并清空 Redis 计数。
    Redis 键格式：日期:分类ID，例如 '2026-03-21:123'
    """
    redis_cli = get_redis_connection('goods_count')

    # 使用 scan_iter 遍历所有键，避免阻塞
    all_keys = list(redis_cli.scan_iter(match='*', count=1000))
    if not all_keys:
        return

    # 聚合相同 (category_id, date) 的计数
    data = {}
    for key in all_keys:
        try:
            # 键格式为 date:category_id，例如 '2026-03-21:123'
            date_str, category_id_str = key.decode().rsplit(':', 1)
            category_id = int(category_id_str)
            # 获取计数（如果键不存在则跳过）
            count = redis_cli.get(key)
            if count is None:
                continue
            count = int(count)
            data[(category_id, date_str)] = data.get((category_id, date_str), 0) + count
        except (ValueError, TypeError) as e:
            print(f"解析 Redis 键失败: {key}, error={e}")
            continue

    if not data:
        return

    # 开始数据库事务
    with transaction.atomic():
        for (category_id, date_str), total in data.items():
            try:
                # 将日期字符串转为 date 对象
                date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()

                # 使用 get_or_create + F 表达式累加
                obj, created = GoodsVisitCount.objects.get_or_create(
                    category_id=category_id,
                    date=date_obj,
                    defaults={'count': total}
                )
                if not created:
                    # 已有记录，使用 F 表达式原子累加
                    GoodsVisitCount.objects.filter(
                        category_id=category_id, date=date_obj
                    ).update(count=F('count') + total)
            except Exception as e:
                print(f"更新数据库失败: category_id={category_id}, date={date_str}, total={total}, error={e}")
                raise  # 抛出异常使事务回滚，避免部分更新

    # 删除所有已处理的 Redis 键
    if all_keys:
        redis_cli.delete(*all_keys)
        print(f"成功合并 {len(data)} 条聚合数据，已删除 {len(all_keys)} 个 Redis 键")
# from datetime import datetime
# from django_redis import get_redis_connection
# from django.db import transaction
#
# from apps.goods.models import GoodsVisitCount
#
#
# def merage_redis_goods_count():
#     redis_cli=get_redis_connection('goods_count')
#     all_keys = redis_cli.keys('*')
#     if len(all_keys)==0:
#         return
#     data={}
#     for key in all_keys:
#         date,category_id=key.split(':')
#         category_id=int(category_id)
#         count=int(redis_cli.get(key))
#         data[(category_id, date)] = data.get((category_id, date), 0) + count
#     with transaction.atomic():
#         for (category_id, date_str), total in data.items():
#             # 转换为日期对象
#             date = datetime.strptime(date_str, '%Y-%m-%d').date()
#             # 使用 update_or_create 原子更新
#             GoodsVisitCount.objects.update_or_create(
#                 category_id=category_id,
#                 date=date,
#                 defaults={'count': total}  # 注意：如果数据库已有数据，会替换成 total，而不是累加
#             )
#     redis_cli.delete('*')