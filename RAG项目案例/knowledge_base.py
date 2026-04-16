import hashlib
import os
from datetime import datetime

from langchain_chroma import Chroma
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

import config

def check_md5(data:str):
    #检查上传到md5字符串是否已经上传过
    if not os.path.exists(config.MD5_PATH):
        open(config.MD5_PATH, 'w').close()
        return False
    for i in open(config.MD5_PATH, 'r').readlines():
        i=i.strip()
        if i==data:
            return True
    return False
def save_md5(data:str):
    '''把传入的md5字符串存入文件'''
    with open(config.MD5_PATH, 'a') as f:
        f.write(data)
def get_string_md5(input: str | bytes):
    if isinstance(input, bytes):
        md5_obj = hashlib.md5()
        md5_obj.update(input)
        return md5_obj.hexdigest()
    else:
        str_bytes = input.encode('utf-8')
        md5_obj = hashlib.md5()
        md5_obj.update(str_bytes)
        return md5_obj.hexdigest()
class KnowledgeBaseServer:
    def __init__(self):
        #向量存储数据库实例
        os.makedirs(config.persist_directory, exist_ok=True)
        self.chroma=Chroma(
            collection_name=config.collection_name,#类似数据库表名
            embedding_function=DashScopeEmbeddings(model="text-embedding-v4"),#嵌入模型，把数据转为向量所用的模型
            persist_directory=config.persist_directory#指定数据存放的文件夹
                )
        #文本分割器，把传入的大数据分割为小的数据
        self.spliter=RecursiveCharacterTextSplitter(
            chunk_size=config.chunk_size,#分割后文本最大长度
            chunk_overlap=config.chunk_overlap,#允许文本重叠的最大字符数，防止语义过于割裂
            separators=config.separators#进行语义划分的符号
        )
    def upload_by_str(self,data,filename)->str:
        '''把传入的数据转为向量并存入向量数据库'''
        md5_str=get_string_md5(data)
        if check_md5(md5_str):
            return "跳过，该数据已经存储"
        if len(data)<config.max_split_char_number:
            #不分割
            knowledge_chuck=[data]
        else:
            knowledge_chuck=self.spliter.split_text(data)#返回list[str]
        metadatas={
            "source":filename,#文件来源
            "creat_time":datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "author":config.author,#文件来源作者
        }
        self.chroma.add_texts(texts=knowledge_chuck,metadatas=[metadatas for _ in knowledge_chuck])
        save_md5(md5_str)
        return "存入数据库成功"

server=KnowledgeBaseServer()
# a=server.upload_by_str("周杰伦","test_file")
# print(a)#打印"存入数据库成功"