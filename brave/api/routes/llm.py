import asyncio
from fastapi import APIRouter, Depends, HTTPException
# from flask import json
import json
from pydantic import BaseModel
import openai
import os
from fastapi.responses import StreamingResponse
from brave.api.enum.component_script import ScriptName
from brave.api.llm.streaming_tool_handler import StreamingToolHandler
from brave.api.llm.tool_manager import ToolManager
from brave.api.service import analysis_service, chat_history_service
from brave.api.service import analysis_result_service
import brave.api.service.pipeline as  pipeline_service
from brave.api.config.db import get_engine
from brave.api.schemas.chat_history import ClearChatHistory, CreateChatHistory, QueryChatHistory
from brave.api.utils.lock_llm import BizProjectLock
from brave.api.llm.schemas.llm import ChatRequest
from dependency_injector.wiring import Provide
from dependency_injector.wiring import inject
from brave.api.llm import llm_service
from brave.app_container import AppContainer

# DeepSeek 官方兼容 OpenAI SDK
# openai.api_base = "https://api.deepseek.com/v1"
# openai.api_key =  "sk-" #os.getenv("DEEPSEEK_API_KEY")
llm_api = APIRouter(prefix="/llm", tags=["llm"])

api_key = os.getenv("API_KEY","")

# client = openai.OpenAI(
#         api_key=api_key,
#         base_url="https://api.deepseek.com",
#     )
client = openai.OpenAI(
        api_key=api_key,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )
# message:nextContent,
# biz_id: biz_id,
# biz_type: biz_type,
# project_id:project

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get weather of a location, the user should supply a location first.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    }
                },
                "required": ["location"]
            },
        }
    },
]

system_prompt = """
The user will provide some exam text. Please parse the "question" and "answer" and output them in JSON format. 

EXAMPLE INPUT: 
Which is the highest mountain in the world? Mount Everest.

EXAMPLE JSON OUTPUT:
{
    "question": "Which is the highest mountain in the world?",
    "answer": "Mount Everest"
}
"""

@llm_api.post("/chat")
async def chat(req: ChatRequest):
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            tools=tools,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": req.message},
            ]
        )
        reply = response.choices[0].message.content
        return {"reply": reply}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# curl -X POST "https://localhost:5005/brave-api/llm/chat" \
#   -H "Content-Type: application/json" \
#   -d '{"message": "你好，介绍一下DeepSeek"}'


@llm_api.post("/chat/stream-test")
async def chat_stream( req: ChatRequest):
    """
    流式返回 DeepSeek 响应
    """

    async def stream():
        try:
            # 使用新版 SDK 的 stream=True
            with client.chat.completions.stream(
                model="deepseek-chat",
                tools=tools,
                # response_format={
                #     'type': 'json_object'
                # },
                messages=[
                    # {"role": "system", "content":system_prompt},
                    {"role": "user", "content": req.message},
                ],
            ) as completion:
                for event in completion:
                    if event.type == "message":
                        # 完整消息一次性输出（可改为逐段输出）
                        yield event.message.content
                    elif event.type == "content.delta":
                        # 模型输出的每一小段（类似 ChatGPT 打字机效果）
                        yield event.delta
                    elif event.type == "error":
                        yield f"[Error] {event.error}"
                    await asyncio.sleep(0)  # 让事件循环更流畅

        except Exception as e:
            yield f"[Server Error] {str(e)}"

    return StreamingResponse(stream(), media_type="text/event-stream")

system_prompt = """
You are an expert in bioinformatics data analysis.


"""
# 如果用户要求：
# - 分析错误
# - 查看报错原因
# - 分析失败
# - 日志是什么
# 你必须自动调用工具 get_error_log(biz_id, biz_type)，不要自己编造答案。
template = """
Use the context below to answer the question.
If a user's question is irrelevant to the context, please encourage the user to ask a question that is relevant to the context.
If users ask code-related questions, please obtain the code from the code section.

Code:
{code}

Context:
{context}

Data:
{data}

Question:
{question}

"""




async def lock_wrapper(biz_id, project_id, gen):
    async with BizProjectLock(biz_id, project_id):
        async for item in gen:
            yield item



tools = [
    {
        "type": "function",
        "function": {
            "name": "get_error_log",
            "description": "根据 biz_id 和 biz_type 查询任务运行日志或错误信息",
            "parameters": {
                "type": "object",
                "properties": {
                    "biz_id": {"type": "string"},
                    "biz_type": {"type": "string"},
                },
                "required": ["biz_id", "biz_type"]
            }
        }
    }
]

async def tool_get_error_log(biz_id: str, biz_type: str):
    # 这里你用自己的 log 系统查询
    # log = query_log_from_db_or_file(biz_id, biz_type)
    log ="模拟的日志内容"
    return log or "未查询到相关日志。"


@llm_api.post("/chat/stream")
@inject
async def chat_stream(req: ChatRequest,
                      tool_manager: ToolManager= Depends(Provide[AppContainer.tool_manager])):
    
    biz_id = req.biz_id
    project_id = req.project_id
    biz_type = req.biz_type
    model_name = req.model_name
    
   

    handler:StreamingToolHandler = StreamingToolHandler( model_name,tool_manager)

    return await handler.run(
        req=req,
        biz_id=biz_id,
        biz_type=biz_type,
        project_id=project_id,
    )

@llm_api.post("/chat/stream2")
async def chat_stream2(req: ChatRequest):

    biz_id = req.biz_id
    biz_type= req.biz_type
    project_id= req.project_id
    """
    流式返回 DeepSeek 响应
    """
    async def stream():
        content = await llm_service.build_prompt(req,system_prompt,template)

        assistant_message = ""  # 最终累积模型输出
        try:
            # 使用新版 SDK 的 stream=True
            with client.chat.completions.stream(
                model="deepseek-chat",
                tools=tools,
                # response_format={
                #     'type': 'json_object'
                # },
                messages=[
                    {"role": "system", "content":system_prompt},
                    {"role": "user", "content": content},
                ],
            ) as completion:
                pending_tool_calls = []
                for event in completion:
                    print(event.type)
                    if event.type == "message":
                        assistant_message += event.message.content
                        # 完整消息一次性输出（可改为逐段输出）
                        yield event.message.content
                    elif event.type == "content.delta":
                        assistant_message += event.delta
                        # 模型输出的每一小段（类似 ChatGPT 打字机效果）
                        # yield event.delta
                        yield f"event: message\ndata: {json.dumps({'content': event.delta})}\n\n"
                    elif event.type == "tool_calls.function.arguments.delta":
                        # pending_tool_calls.append(event)
                        pass
                    elif event.type == "tool_calls.function.arguments.done":
                        pending_tool_calls.append(event)
                    elif event.type == "error":
                        yield f"[Error] {event.error}"
                    await asyncio.sleep(0)  # 让事件循环更流畅
                   # --------------------------
                
                
                # 处理工具调用（可能多个）
                # --------------------------
                if pending_tool_calls:
                    tool_results = []
                    for tc in pending_tool_calls:
                        func = tc.function.name   # get_error_log
                        args = json.loads(tc.function.arguments)

                        if func == "get_error_log":
                            result = await tool_get_error_log(
                                args["biz_id"], args["biz_type"]
                            )
                            tool_results.append({
                                "role": "tool",
                                "tool_call_id": tc.id,
                                "name": func,
                                "content": result
                            })

                    # ✔ 把工具结果继续发给 LLM，让 LLM 继续回答
                    follow_messages = [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": content},
                        *tool_results
                    ]
                    pass
                with get_engine().begin() as conn:
                    create_chatHistory = CreateChatHistory(
                        user_id=None,
                        session_id=None,
                        biz_id=biz_id,
                        biz_type=biz_type,
                        role="assistant",
                        content=assistant_message,
                        project_id=project_id,
                    )
                    chat_history_service.insert_chat_history(conn, create_chatHistory)
                # print("Final assistant message:", assistant_message)

        except Exception as e:
            yield f"[Server Error] {str(e)}"

    async with BizProjectLock(req.biz_id, req.project_id):
        # return StreamingResponse(stream(), media_type="text/event-stream")
        return StreamingResponse(
            lock_wrapper(req.biz_id, req.project_id, stream()),
            media_type="text/event-stream"                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       
        )

# curl -N -k -X POST "https://localhost:5005/brave-api/llm/chat/stream" \
#   -H "Content-Type: application/json" \
#   -d '{"message": "你好，介绍一下精准医学"}'


# @llm_api.post("/chat/stream")
# async def chat_stream(req: ChatRequest):
#     async def stream():
#         completion = await openai.ChatCompletion.acreate(
#             model="deepseek-chat",
#             messages=[{"role": "user", "content": req.message}],
#             stream=True,
#         )
#         async for chunk in completion:
#             if chunk.choices and chunk.choices[0].delta.get("content"):
#                 yield chunk.choices[0].delta.content
#     return StreamingResponse(stream(), media_type="text/event-stream")


@llm_api.post("/chat/history")
async def chat_history(queryChatHistory: QueryChatHistory):
    with get_engine().begin() as conn:
        chat_history = chat_history_service.get_chat_history_by_project_id_and_biz_id(
            conn, queryChatHistory)
    return chat_history


@llm_api.post("/chat/history/clear")
async def clear_chat_history(clearChatHistory: ClearChatHistory):
    with get_engine().begin() as conn:
        chat_history_service.clear_chat_history(
            conn, clearChatHistory)
    return {"message": "Chat history cleared."}

@llm_api.delete("/chat/history/del-by-chat-history-id/{chat_history_id}")
async def delete_chat_history_by_id(chat_history_id: str):
    with get_engine().begin() as conn:
        stmt = chat_history_service.delete_chat_history_by_id(conn, chat_history_id)
    return {"message": f"Chat history with id {chat_history_id} deleted."}