# from fdfs_client.client import Fdfs_client
# #1.加载客户端，加载配置文件（若本机IP变化要修改配置文件的IP）
# client=Fdfs_client('/home/tom/桌面/django_project/meiduo/meiduo_shop/utils/fastdfs/client.conf')
# #2.上传图片，填写图片绝对路径
# client.upload_by_filename('/home/tom/下载/a.png')
# #3.获取filed_id,上传成功会返回字典数据，里面有获取filed_id
# """getting connection
# <fdfs_client.connection.Connection object at 0x7e1cf755a1b0>
# <fdfs_client.fdfs_protol.Tracker_header object at 0x7e1cf755a210>
# {'Group name': 'group1', 'Remote file_id': 'group1/M00/00/00/wKjcgWlve-CAAdCwAAHfZWN5nwc250.png',
# 'Status': 'Upload successed.', 'Local file name': '/home/tom/下载/a.png',
# 'Uploaded size': '119.00KB', 'Storage IP': '192.168.220.129'}"""
# a,b,x,y=map(int,input().split())
# import sys
#
# input=sys.stdin.readline
# n,m=map(int,input().split())
# list_n=list(map(int,input().split()))
# s_m=[]
# for i in range(m):
#     s_m.append(list(map(int,input().split())))
# t_m=[]
# for i in range(m):
#     t_m.append(list(map(int,input().split())))
#
#
# for j in range(m):
#     p = 1
#     if(s_m[j][0]!=t_m[j][0]):
#         print('wrong')
#         continue
#     else:
#         s=1
#         while(p<=s_m[j][0]):
#             if s_m[j][p]!=t_m[j][p]:
#                 s=0
#                 break
#             p+=1
#         p=1
#         while True:
#             x=list_n[s_m[j][p]-1]
#             y=list_n[t_m[j][p]-1]
#             while p+1<=s_m[j][0]:
#                 x=x^list_n[s_m[j][p+1]-1]
#                 y=y^list_n[t_m[j][p+1]-1]
#                 p=p+1
#             break
#         if x==y and s==1:
#             print('correct')
#         elif x!=y and s==0:
#             print('correct')
#         else:
#             print('wrong')
import heapq
import math

from collections import Counter, defaultdict
from copy import deepcopy

from celery.worker.strategy import default

# import sys
# def test_2(data,n,m):
#     num=[]
#     for i in range(m):
#         for j in range(n):
#             num.append(data[j*m+i])
#     return num
# if __name__ == "__main__":
#     input = sys.stdin.readline
#     n,m,t = list(map(int, input().split()))
#     data=[]
#     for line in range(n):
#         nums = list(map(int, input().split()))
#         data.extend(nums)  # 或 data += nums
#     for i in range(t):
#         op,a,b= list(map(int, input().split()))
#         if op==1:
#
#             n,m=a,b
#
#         elif op==2:
#
#             data=test_2(data,n,m)
#             m,n=n,m
#
#         elif op==3:
#
#             print(data[a*m+b])
# import sys
# from functools import partial, lru_cache
# @lru_cache(maxsize=None)
# def f(b,k):
#     num=(b*b+k*k)%8
#     ans=num^k
#     return ans
#
# def solve():
#     input = sys.stdin.readline
#     n, m = map(int, input().split())
#     # 要求n个数的输入值
#     list_k = list(map(int, input().split()))  # 有m个
#     list_k.reverse()
#     list_a = list(map(int, input().split()))  # 有n个
#     ans=[0]*513
#     for i in range(513):
#         # 求i的输入值
#         x = i
#
#         for k in list_k:
#             # 由k计算当前的c和a
#             b = (x >> 6) & 0b111
#             mid = (x >> 3) & 0b111
#             right = x & 0b111
#
#             num_1 = f(b, k)
#             c = num_1 ^ mid
#             num_2 = f(c, k)
#             a = num_2 ^ right
#             x = (a << 6) + (b << 3) + c
#         ans[i]=x
#
#     for i in list_a:
#         print(ans[i],end=' ')
# if __name__ == '__main__':
#     solve()
# import sys
# import math
# input=sys.stdin.readline
# n,a=map(int,input().split())
# test=[list(map(float,input().split())) for i in range(n)]
# m=0
# for i in range(len(test)):
#     x=test[i][0]
#     y=test[i][1]
#     t=math.sqrt(x*x+y*y)
#     if t<=a:
#         m+=1
# ans=(4*m)/n
# sys.stdout.write(str(ans)+'\n')

# import sys
# input=sys.stdin.readline
# n,l=map(int,input().split())
# test_list=[list(map(int,input().split())) for i in range(n)]
# ans=set()
# i,j=0,0
# # min_test=[0]*29
# # max_test=[0]*16
# #图像 A是否包含一个大小为 5×9的子矩阵
# while i<n and i+4<n:
#     #i是行号
#     j=0
#     while j<n and j+8<n:
#         #j是列号
#         min_test=min(test_list[i][j],test_list[i][j+1],test_list[i][j+2],
#         test_list[i][j+3],test_list[i][j+4],test_list[i][j+5],test_list[i][j+6],
#         test_list[i][j+7],test_list[i][j+8],test_list[i+1][j],test_list[i+1][j+3],
#                      test_list[i+1][j+6],test_list[i+1][j+8],
#                      test_list[i+2][j],test_list[i+2][j+3],test_list[i+2][j+4],test_list[i+2][j+5],
#                      test_list[i+2][j+6],test_list[i+2][j+7],test_list[i+3][j],test_list[i+3][j+5],
#                      test_list[i+3][j+6],test_list[i+4][j],test_list[i+4][j+1],test_list[i+4][j+2],
#                      test_list[i+4][j+3],test_list[i+4][j+4],test_list[i+4][j+5],test_list[i+4][j+6])
#         max_test=max(test_list[i+1][j+1],test_list[i+1][j+2],test_list[i+1][j+4],test_list[i+1][j+5],test_list[i+1][j+7],
#                      test_list[i+2][j+1],test_list[i+2][j+2],test_list[i+2][j+8],
#                      test_list[i+3][j+1],test_list[i+3][j+2],test_list[i+3][j+3],test_list[i+3][j+4],test_list[i+3][j+7],test_list[i+3][j+8],
#                      test_list[i+4][j+7],test_list[i+4][j+8])
#         if min_test<=max_test:
#             j+=1
#         else:
#             num=max_test+1
#             ans.add(num)
#             for num in range(max_test + 1, min_test + 1):
#                 ans.add(num)
#             if j + 9 >= n:
#                 break
#             else:
#                 j += 9
#     i+=1
# ss=sorted(ans)
# a=[str(i) for i in ss]
# sys.stdout.write('\n'.join(a)+'\n')


'''方法1'''
# input=sys.stdin.readline
# n,m=map(int,input().split())
#
# num=[]
# for i in range(n):
#     data=list(map(int,input().split()))
#     mm=[0]*(m+1)
#     for j in data[1:]:
#         mm[j]+=1
#     num.append(mm)
#
# for i in range(1,m+1):
#     x,y=0,0
#     for j in num:
#
#         if j[i]==0:
#             continue
#         else:
#             x+=1
#             y+=j[i]
#     print(x,y)
# '''方法2'''
# input=sys.stdin.readline
# n,m=map(int,input().split())
# x=[0]*(m+1)#该单词文章数
# y=[0]*(m+1)#该单词出现次数
# article=[0]*(m+1) # 最后出现文章编号
# for article_id in range(1,n+1):
#     data=list(map(int,input().split()))
#     words=data[1:]
#     for word in words:
#         if article[word]!=article_id:
#             x[word]+=1
#             article[word]=article_id
#         y[word]+=1
# for i in range(1,m+1):
#     print(x[i],y[i])

# import sys
# import math
#
# MOD = 998244353
#
# def solve() -> None:
#     input = sys.stdin.readline
#     n = int(input())
#     a = list(map(int, input().split()))
#
#     ans = 0
#     seg = []                     # 列表元素 (g, l)，l 是该段的最小左端点，列表按 l 递减
#
#     for r in range(1, n + 1):
#         val = a[r - 1]
#         new_seg = [(val, r)]     # 当前右端点单独构成一段
#
#         # 合并上一轮的段，更新 gcd
#         for g, l in seg:
#             new_g = math.gcd(g, val)
#             if new_g == new_seg[-1][0]:
#                 # 相同的 gcd 合并，取更小的左端点
#                 new_seg[-1] = (new_g, l)
#             else:
#                 new_seg.append((new_g, l))
#
#         seg = new_seg
#
#         # 计算以 r 为右端点的所有区间的贡献
#         for i, (g, l) in enumerate(seg):
#             if i == 0:
#                 upper = r                # 最右边的段一直延伸到 r
#             else:
#                 upper = seg[i - 1][1] - 1  # 上一个段的最小左端点减一
#             lower = l
#             cnt = upper - lower + 1
#             sum_l = (lower + upper) * cnt // 2   # 等差数列求和
#             ans = (ans + r * g * sum_l) % MOD
#
#     print(ans)
#
# if __name__ == "__main__":
#     solve()
# from collections import defaultdict
# import math
# import sys
# input=sys.stdin.readline
# '''f(x)=x*x+b*x+c'''
# n=int(input())#分别表示苹果总数和每天最大投喂量
# ans=defaultdict(str)
# bianliang=set()
# for i in range(n):
#     data=list(map(str,input().split()))
#     num=data[0]
#     bianliang.add(data[1])
#     var=''
#
#     if num=='1' :
#         for value in data[2:]:
#             if '$' in value:
#                 if value[1:] in bianliang:
#                     ans[data[1]] = ans[data[1]] +ans[value[1:]]
#                 else:
#                     ans[data[1]]=ans[data[1]]+value[1:]
#             else:
#                 ans[data[1]]=ans[data[1]]+value
#     elif num=='2' :
#         for value in data[2:]:
#             if '$' in value:
#                 if value[1] in bianliang:
#                     ans[data[1]] = ans[data[1]] +ans[value[1:]]
#
#     elif num=='3':
#         print(len(ans[data[1]]))
# import sys
# input=sys.stdin.readline
# n,m=map(int,input().split())
# a=list(map(int,input().split()))
# #f[i] 表示容量为 i 时的最大价值
# f=[0]*(n+1)
# for i in range(1,n+1):
#     for j in range(1,min(i,m)+1):
#         f[i]=max(f[i],f[i-j]+a[j-1])
# print(f[n])
# import sys
# import math
#
# N = 998244353
#
# def solve() -> None:
#     input = sys.stdin.readline
#     n = int(input())
#     a = list(map(int, input().split()))
#
#     ans = 0
#     prev = []          # 每个元素为 (gcd, 左端点起始)，按左端点从小到大排列
#
#     for j in range(n):
#         cur = []
#         # 利用上一轮的段，得到新段
#         for g, l in prev:
#             ng = math.gcd(g, a[j])
#             if cur and cur[-1][0] == ng:
#                 # 与前一段gcd相同，合并（保留更左的起点）
#                 continue
#             cur.append((ng, l))
#
#         # 处理以j为左端点的子数组
#         if not cur or cur[-1][0] != a[j]:
#             cur.append((a[j], j))
#
#         # 计算以j为右端点的所有子数组的贡献
#         for idx in range(len(cur)):
#             g, l = cur[idx]
#             # 确定该段覆盖的左端点范围 [l, r]
#             if idx + 1 < len(cur):
#                 r = cur[idx + 1][1] - 1
#             else:
#                 r = j
#             cnt = r - l + 1
#             # 求和 (i+1) for i from l to r
#             sum_i1 = (l + 1 + r + 1) * cnt // 2
#             ans = (ans + (j + 1) * g % N * (sum_i1 % N)) % N
#
#         prev = cur
#
#     print(ans)
#
# if __name__ == "__main__":
#     solve()
# import sys,math
# from collections import defaultdict
# input=sys.stdin.readline
# n,L,S=map(int,input().split())
# site=set()
# for i in range(n):
#     x,y=map(int,input().split())
#     site.add((x,y))
# ans=[]
# for i in range(S+1):
#     a=list(map(int,input().split()))
#     ans.append(a)
# ans.reverse()
# test_ans=[]
# num=0
# for x,y in site:
#     flag = 0
#     for i in range(S+1):
#         for j in range(S+1):
#             p=ans[i][j]
#             if p==1:
#                 if i+x>L or j+y>L or (i+x,j+y) not in site:
#                     flag=1
#                     break
#             else:
#                 if i+x>L or j+y>L or (i+x,j+y) in site:
#                     flag=1
#                     break
#         if flag==1:
#             break
#     if flag==0:
#         num+=1
# print(num)
# import sys
# input=sys.stdin.readline
# a=list(map(int,input().split()))
# pre=0
# ans=0
# flag=0
# for i in range(len(a)):
#     if a[i]==0:
#         break
#     num=a[i]
#     if num==1:
#         ans+=1
#         flag=0
#     elif num==2:
#         if flag==0:
#
#             flag+=1
#             ans += flag*2
#         else:
#             flag += 1
#             ans+=flag*2
#
# print(ans)
#
# import math
# n,m=map(int,input().split())
# a=list(map(int,input().split()))
# num=0
# test=[0]*n
# flexable_words=n-m-9
# rock=[]#存放空隙的大小
# now_rock=a[0]-1
# test[now_rock-1]=1
# #存放空隙的大小,起始下标，终止下标
# rock.append((now_rock,0,a[0]-2))
# for i in range(1,len(a)):
#     test[a[i]-1]=1
#     now_rock=a[i]-a[i-1]-1
#     if now_rock>0:
#         rock.append((now_rock,a[i-1],a[i]-2))
# if a[-1]!=n:
#     rock.append((n-a[-1], a[-1],n-1 ))
# for x in range(len(rock)):
#     total,i,j=rock[x][0],rock[x][1],rock[x][2]
#     if total>=3:
#         for xx in range(i,j+1):
#             flax_word = j-xx-2
#             if flax_word>=0:
#                 if flax_word >= 6:
#                     x_num=flax_word-6+1
#                     num += math.pow(26, flexable_words)*x_num % 998244353
#                 else:
#                     for y in range(x + 1, len(rock)):
#                         if rock[y][0] >= 6:
#                             y_num=rock[y][0]-6+1
#                             num += math.pow(26, flexable_words)*y_num % 998244353
# print(num)




