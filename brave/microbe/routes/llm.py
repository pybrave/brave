import asyncio
from fastapi import APIRouter, FastAPI, HTTPException
from pydantic import BaseModel
import openai
import os
from fastapi.responses import StreamingResponse

# DeepSeek 官方兼容 OpenAI SDK
# openai.api_base = "https://api.deepseek.com/v1"
# openai.api_key =  "sk-" #os.getenv("DEEPSEEK_API_KEY")
api_key = os.getenv("DEEPSEEK_API_KEY","")
llm_api = APIRouter(prefix="/llm", tags=["llm"])
client = openai.OpenAI(
            api_key=api_key,
        base_url="https://api.deepseek.com/v1",
    )
class ChatRequest(BaseModel):
    message: str

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


@llm_api.post("/chat/stream")
async def chat_stream(req: ChatRequest):
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