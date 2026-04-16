# from langchain_chroma import Chroma
# from langchain_community.chat_models import ChatTongyi
# from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
# from langchain_community.embeddings import DashScopeEmbeddings
# model=ChatTongyi(model="qwen3-max")
# prompt=ChatPromptTemplate.from_messages(
#     [
#         ("system","以我提供的参考资料为主简洁专业的回答用户问题，参考资料{content}"),
#         MessagesPlaceholder("history_chart"),
#         ("human","用户提问:{input}")
#     ]
# )
# vector_store=Chroma(
#     collection_name="test",#类似数据库表名
#     embedding_function=DashScopeEmbeddings(),#嵌入模型，把数据转为向量所用的模型
#     persist_directory="./chrom_db"#指定数据存放的文件夹
# )
# #向量存储对象通过as_retriever返回一个Runnable子类对象
# retriever=vector_store.as_retriever(search_kwargs={"k":2})