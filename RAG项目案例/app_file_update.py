import asyncio
import sys
import os

from pydantic import BaseModel
from starlette.responses import StreamingResponse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import uuid
from config import UPLOAD_DIR
from knowledge_base import server
from fastapi import FastAPI, UploadFile, File, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
app=FastAPI()

# 允许跨域（开发环境）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # 生产环境应指定具体前端地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
ALLOWED_EXTENSIONS = {
    "pdf", "txt", "md", "doc", "docx", "pptx", "xlsx", "csv", "json", "html", "xml", "markdown"
}
def validate_file(file:UploadFile):
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    #检查文件是否合法
    if file.filename.split(".")[-1].lower() not in ALLOWED_EXTENSIONS:
        return False
    return True

@app.post('/api/rag/upload')
async def get_file(file:UploadFile=File(...)):
    try:
        if not validate_file(file):
            return JSONResponse(status_code=400,content={'message':"文件格式错误"})
        #保存文件
        #1.生成文件唯一id
        ext=file.filename.split(".")[-1].lower()
        file_name=f"{uuid.uuid4()}.{ext}"
        file_path=os.path.join(UPLOAD_DIR,file_name)
        #读入文件
        content=await file.read()
        print(file_path)

        # content_str = content_bytes.decode('utf-8')
        with open(file_path,"wb") as f:
            f.write(content)
        #利用知识库类写入向量数据库

        content_str = content.decode('utf-8')
        a=server.upload_by_str(content_str, file_path)
        print(a)
        #读取文件内容
        return {
                    "code": 200,
                    "message": "success",
                    "data": {
                        "fileId": file_name.replace(f".{ext}", ""),  # 去掉扩展名的 UUID
                        "url": f"/storage/{file_name}",              # 静态资源路径
                        "originalName": file.filename
                    }
                }
    except Exception as e:
        print(f"上传失败: {type(e).__name__} - {e}")
        return JSONResponse(status_code=400, content={'message': f"服务器错误: {str(e)}"})
from vector_stores import qa_chain
class ChatRequest(BaseModel):
    query: str
@app.post('/api/chat/stream')
async def chat_stream(request: ChatRequest):
    async def generate():
        try:
            # 异步调用链（这里假设 qa_chain 有 ainvoke 方法）
            # 注意：RetrievalQA 的 ainvoke 可能不会流式输出，需要底层 LLM 支持流式并正确传递
            # 更可靠的方法是使用自定义异步流式链
            result = await qa_chain.ainvoke({"query": request.query})
            answer = result.get("result", "")
            # 将完整答案分块发送（模拟流式）
            chunk_size = 30
            for i in range(0, len(answer), chunk_size):
                yield f"data: {answer[i:i+chunk_size]}\n\n"
                await asyncio.sleep(0.02)
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: 抱歉，处理出错：{str(e)}\n\n"
            yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")