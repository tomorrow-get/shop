from langchain_community.chat_models import ChatTongyi
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableWithMessageHistory, RunnableLambda
from openai import conversations

from RAG项目案例.file_history_story import get_history
from vector_stores import vector_store
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


class RagServer:
    def __init__(self):
        self.vector_store=vector_store#获取向量服务类
        #提示词模板
        self.prompt_template=ChatPromptTemplate.from_messages(
            [
                    ("system","以我提供的参考资料为主简洁专业的回答用户问题，参考资料{content}"),
                    ("system", "并且我提供用户的会话历史记录如下"),
                    MessagesPlaceholder("history"),
                    ("user","请回答用户提问:{input}")
                ]
        )
        #聊天模型
        self.chat_model=ChatTongyi(model="qwen3-max")
        self.chain=self.__get_chain()

    def __get_chain(self):
        """获取最终的执行链"""

        def get_str(doc: list[Document]):
            if not doc:
                return "没有参考资料"
            target = ""
            for i in doc:
                target += f"文档片段：{i.page_content}\n文档元数据：{i.metadata}\n\n"
            return target

        def extract_query_text(data: dict) -> str:
            """
            从 RunnableWithMessageHistory 传下来的 input 中提取纯文本问题。
            兼容：
            1) data["input"] 是 [HumanMessage(...)]
            2) data["input"] 是字符串
            """
            x = data["input"]
            if isinstance(x, list):
                if not x:
                    return ""
                first = x[0]
                return first.content if hasattr(first, "content") else str(first)
            return str(x)

        def format_for_prompt(data: dict) -> dict:
            """
            只做字段整理，不要丢 history。
            """
            return {
                **data,  # 保留 history、content 等所有字段
                "input": extract_query_text(data),  # prompt 里用纯文本
            }
        #获取相似度检索后返回的值
        vetriever = self.vector_store.get_vector()

        chain = (
                RunnablePassthrough()
                .assign(
                    content=RunnableLambda(lambda data: extract_query_text(data)) | vetriever | get_str
                )
                | RunnableLambda(format_for_prompt)
                | self.prompt_template
                | self.chat_model
                | StrOutputParser()
        )

        conversation_chain = RunnableWithMessageHistory(
            chain,
            get_history,
            input_messages_key="input",
            history_messages_key="history",
        )
        return conversation_chain
if __name__ == '__main__':
    session_config={
        "configurable":{
            "session_id":"user001"
        }
    }
    #传入session_id因为一个用户一个会话历史记录
    q=RagServer().chain.invoke({"input":"王嘉合有什么荣誉"},session_config)
    print(q)
