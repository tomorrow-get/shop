import os

BASE_DIR=r"C:\Users\Tom\Desktop\rag_test\RAG项目案例"
MD5_PATH = os.path.join(BASE_DIR, "chrom_db_md5")
collection_name="test"#类似用于向量检索的数据库表名
persist_directory = os.path.join(BASE_DIR, "chrom_db")##指定数据存放的文件夹
chunk_size=500
chunk_overlap=50
separators=["\n\n","\n",",",".","!","?","，","。","？","！"," ",""]
max_split_char_number=1000#大于该数字的文本才进行分割
author="xxx"#上传作者，后续可以从request里面获取
UPLOAD_DIR= os.path.join(BASE_DIR, "uploads")#存储管理员上传知识文件的根路径
chart_history_story=os.path.join(BASE_DIR, "chart_history_db")##指定数据存放的文件夹

similarity_threshold=1#进行相似度检索返回的文档数量