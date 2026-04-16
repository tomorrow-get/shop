import sys
'''
用于内存测试
'''
class App:
    def __init__(self,name):
        self.name=name


def memory_reuse_demo():
    # 第一次创建对象
    obj1 = App('test')
    obj1_id = id(obj1)
    print(f"第一个对象ID: {obj1_id}")

    # 删除引用，对象被销毁
    del obj1

    # 立即创建第二个对象
    obj2 = App('test')
    obj2_id = id(obj2)
    print(f"第二个对象ID: {obj2_id}")

    print(f"ID相同吗: {obj1_id == obj2_id}")  # 很可能True


memory_reuse_demo()

