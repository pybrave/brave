import asyncio
from fastapi import APIRouter, HTTPException
# from flask import json
import json
from pydantic import BaseModel
import openai
import os
from fastapi.responses import StreamingResponse
from brave.api.enum.component_script import ScriptName
from brave.api.service import analysis_service, chat_history_service
from brave.api.service import analysis_result_service
import brave.api.service.pipeline as  pipeline_service
from brave.api.config.db import get_engine
from brave.api.schemas.chat_history import CreateChatHistory, QueryChatHistory
from brave.api.utils.lock_llm import BizProjectLock


# DeepSeek 官方兼容 OpenAI SDK
# openai.api_base = "https://api.deepseek.com/v1"
# openai.api_key =  "sk-" #os.getenv("DEEPSEEK_API_KEY")
api_key = os.getenv("DEEPSEEK_API_KEY","")
llm_api = APIRouter(prefix="/llm", tags=["llm"])
client = openai.OpenAI(
            api_key=api_key,
        base_url="https://api.deepseek.com/v1",
    )

# message:nextContent,
# biz_id: biz_id,
# biz_type: biz_type,
# project_id:project
class ChatRequest(BaseModel):
    message: str
    biz_id: str = None
    biz_type: str = None
    project_id: str = None
    is_save_prompt: bool = False

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

def build_prompt(req: ChatRequest):
    biz_id = req.biz_id
    biz_type= req.biz_type
    project_id= req.project_id
    context =""
    code =""
    data =""

    with get_engine().begin() as conn:
        if biz_type=="tools":
            find_relation = pipeline_service.find_relation_component_prompt_by_id(conn, biz_id)
            if find_relation:
                if find_relation["prompt"]:
                    context = find_relation["prompt"]
            
                component_script = pipeline_service.find_component_module(find_relation,ScriptName.main)['path']
                if os.path.exists(component_script):
                    with open(component_script, "r") as f:
                        code = f.read()
        elif biz_type=="script":
            component = pipeline_service.find_component_by_id(conn, biz_id)
            if component:
                if component["prompt"]:
                    context = component["prompt"]
                
                component_script = pipeline_service.find_component_module(component,ScriptName.main)['path']
                if os.path.exists(component_script):
                    with open(component_script, "r") as f:
                        code = f.read()
        elif biz_type =="file":
            component = pipeline_service.find_component_by_id(conn, biz_id)
            # find_result = analysis_result_service.find_component_and_analysis_result_by_analysis_result_id(conn, biz_id)
            if component:

                # file_type = component["file_type"]
                # file_content = component["content"]
                prompt = component["prompt"]
                if prompt:
                    context = prompt
                content = component["content"]
                if content:
                    data = content
        elif biz_type =="analysis_result":
            find_result = analysis_result_service.find_component_and_analysis_result_by_analysis_result_id(conn, biz_id)
            if find_result:
                
                file_type = find_result["file_type"]
                file_content = find_result["content"]
                component_prompt = find_result["component_prompt"]
                if component_prompt:
                    context = component_prompt

                if file_type =="collected" and os.path.exists(file_content):
                    with open(file_content, "r") as f:
                        data = "".join([line for _, line in zip(range(100), f)])
                else:
                    data = file_content
                    


        elif biz_type =="analysis":
            find_analysis = analysis_service.find_analysis_and_component_by_id(conn, biz_id)
            if  find_analysis:
                # raise HTTPException(status_code=404, detail="Analysis not found")
                output_dir = find_analysis["output_dir"]
                prompt = f"{output_dir}/output/prompt.ai"
                if find_analysis["relation_prompt"]:
                    context = find_analysis["relation_prompt"]
                if os.path.exists(prompt):
                    prompt0 = "The analysis results are as follows:\n"
                    with open(prompt, "r") as f:
                        data =  prompt0 + f.read()
                if find_analysis["pipeline_script"]:
                    component_script = find_analysis["pipeline_script"]
                    if os.path.exists(component_script):
                        with open(component_script, "r") as f:
                            code = f.read()

        
        content = template.format(context=context,
                                code=code,
                                data=data,
                                question=req.message)
        create_chatHistory = CreateChatHistory(
                user_id=None,
                session_id=None,
                biz_id=biz_id,
                biz_type=biz_type,
                role="user",
                content=req.message,
                project_id=project_id,
            )
            # system_prompt=system_prompt,
            # user_prompt=content,
        if req.is_save_prompt:
            create_chatHistory.system_prompt=system_prompt
            create_chatHistory.user_prompt=content
        chat_history_service.insert_chat_history(conn, create_chatHistory)
    return content
async def lock_wrapper(biz_id, project_id, gen):
    async with BizProjectLock(biz_id, project_id):
        async for item in gen:
            yield item


@llm_api.post("/chat/stream")
async def chat_stream(req: ChatRequest):

    biz_id = req.biz_id
    biz_type= req.biz_type
    project_id= req.project_id
    """
    流式返回 DeepSeek 响应
    """
    async def stream():
        content = build_prompt(req)

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
                for event in completion:
                    if event.type == "message":
                        assistant_message += event.message.content
                        # 完整消息一次性输出（可改为逐段输出）
                        yield event.message.content
                    elif event.type == "content.delta":
                        assistant_message += event.delta
                        # 模型输出的每一小段（类似 ChatGPT 打字机效果）
                        # yield event.delta
                        yield f"event: message\ndata: {json.dumps({'content': event.delta})}\n\n"

                    elif event.type == "error":
                        yield f"[Error] {event.error}"
                    await asyncio.sleep(0)  # 让事件循环更流畅
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