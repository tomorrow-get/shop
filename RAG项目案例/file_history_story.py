import json
import os.path
from typing import Sequence
from langchain_community.chat_models import ChatTongyi
from langchain_core.messages import message_to_dict, messages_from_dict, BaseMessage
from langchain_core.chat_history import BaseChatMessageHistory
import config
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableWithMessageHistory, RunnableLambda
def get_history(session_id:str):
    return MyFileChartHistory(session_id=session_id,storage_path=config.chart_history_story)
class MyFileChartHistory(BaseChatMessageHistory):
    session_id:str
    storage_path:str
    def __init__(self,session_id:str,storage_path:str):
        self.session_id = session_id
        self.storage_path = storage_path#文件夹路径
        self.file_path=os.path.join(self.storage_path,self.session_id)
        #确保文件夹存在
        os.makedirs(self.storage_path,exist_ok=True)
    def add_messages(self, messages: Sequence[BaseMessage]) -> None:
        all_messages = list(self.messages)
        all_messages.extend(messages)
        dict_message=[message_to_dict(message) for message in all_messages]
        with open(self.file_path,'w') as f:
            json.dump(dict_message,f)

    @property
    def messages(self) -> list[BaseMessage]:
        try:
            with open(self.file_path,'r') as f:
                json_data = json.load(f)#获取的是列表里面的字典
                return messages_from_dict(json_data)#把字典转为消息
        except FileNotFoundError:
            return []
    def clear(self) -> None:
        with open(self.file_path,'w') as f:
            f.write("")
# model=ChatTongyi(model="qwen3-max")
# prompt=ChatPromptTemplate.from_messages(
#     [
#         ("system","你需要根据历史记录回答用户问题"),
#         MessagesPlaceholder("history_chart"),
#         ("human","回答下面问题:{input}")
#     ]
# )
# str_parser=StrOutputParser()
# def print_prompt(full_prompt):
#     print("#"*10+full_prompt.to_string()+"#"*10)
#     return full_prompt
# #LangChain 的 | 操作符会自动将普通函数包装为 RunnableLambda
# base_chain=prompt | RunnableLambda(print_prompt) | model | str_parser
# def get_history(session_id:str):
#     return MyFileChartHistory(session_id=session_id,storage_path="./chart")
# conversation_chain=RunnableWithMessageHistory(
#     base_chain,#被增强的原有链
#     get_history,#通过会话id获取历史记录
#     input_messages_key="input",#表示用户输入在模板中的占位符
#     history_messages_key="history_chart"
# )
# if __name__ == '__main__':
#     session_config={
#         "configurable":{
#             "session_id": "user_001",
#         }
#     }
#     # res=conversation_chain.invoke({"input":"小米有两只猫"},session_config)
#     # print("第一次执行"+res)
#     # res = conversation_chain.invoke({"input": "小米有两只狗"}, session_config)
#     # print("第二次执行"+res)
#     res = conversation_chain.invoke({"input": "小米养了几只宠物"}, session_config)
#     print("第二次执行" + res)
if __name__ == '__main__':
    import os
    from pathlib import Path


    def find_project_root(start_path=None, marker_files=('.git', 'pyproject.toml', 'setup.py')):
        """向上查找包含任意一个 marker_files 的目录作为项目根目录"""
        if start_path is None:
            start_path = Path(__file__).resolve().parent
        for parent in [start_path] + list(start_path.parents):
            for marker in marker_files:
                if (parent / marker).exists():
                    return parent
        return start_path  # 没找到就返回当前脚本目录


    root_dir = find_project_root()
    print(root_dir)