from langchain_chroma import Chroma
from langchain_classic.chains.retrieval_qa.base import RetrievalQA
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_community.llms.tongyi import Tongyi

from config import collection_name,persist_directory,similarity_threshold
class Vector_Store_Service:
    def __init__(self,embedding):
        self.embedding = embedding
        self.vector_store = Chroma(
            collection_name=collection_name,  # 类似数据库表名
            embedding_function=self.embedding,  # 嵌入模型，把数据转为向量所用的模型
            persist_directory=persist_directory  # 指定数据存放的文件夹
        )
    def get_vector(self):
        '''获取向量检索器方便加入后续链条'''
        return self.vector_store.as_retriever(search_kwargs={"k":similarity_threshold})
# if __name__ == '__main__':
#     vector_store = Vector_Store_Service(DashScopeEmbeddings(model="text-embedding-v4")).get_vector()
#     res=vector_store.invoke("王嘉合是谁")
#     print(res)
vector_store = Vector_Store_Service(DashScopeEmbeddings(model="text-embedding-v4"))
# vector_store = Vector_Store_Service(DashScopeEmbeddings(model="text-embedding-v4")).get_vector()
# # 初始化 LLM（开启流式）
# llm = Tongyi(model="qwen-turbo", streaming=True)
#
# # 构建 RAG 链
# qa_chain = RetrievalQA.from_chain_type(
#     llm=llm,
#     retriever=vector_store,
#     return_source_documents=False
# )