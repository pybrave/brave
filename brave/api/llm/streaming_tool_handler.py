# streaming_tool_handler.py
import asyncio
import json
import os
from fastapi.responses import StreamingResponse
import openai

from brave.api.llm.tool_manager import ToolManager
from brave.api.schemas.chat_history import CreateChatHistory
from brave.api.service import chat_history_service
from brave.api.utils.lock_llm import BizProjectLock
from .schemas.llm import ChatRequest
from brave.api.config.db import get_engine

async def lock_wrapper(biz_id, project_id, gen):
    async with BizProjectLock(biz_id, project_id):
        async for item in gen:
            yield item



class StreamingToolHandler:

    def __init__(self, client, tool_manager: ToolManager):
        self.client = client
   #     api_key=self.api_key,
        self.tool_manager = tool_manager
        # self.api_key = os.getenv("DEEPSEEK_API_KEY","")
        # self.client = openai.OpenAI(
          #     base_url="https://api.deepseek.com/v1",
        # )


    async def run(self, messages,biz_id,biz_type, project_id):
        # biz_id = req.biz_id
        # biz_type= req.biz_type
        # project_id= req.project_id
        """
        流式返回 DeepSeek 响应
        """
        async def stream():
            # content = build_prompt(req)
            tools = self.tool_manager.get_schemas()
            # print(tools)

            assistant_message = ""  # 最终累积模型输出
            current_messages = list(messages)
            try:
                while True:
                    # print(current_messages)
                    # print("Starting a new interaction round with the model...\n\n")
                     # ---------- ① 发送消息，获取响应流 ----------
                    pending_tool_calls = []
                    round_text_buffer = ""   # 本轮累积文本
                    with self.client.chat.completions.stream(
                        model="deepseek-chat",
                        # stream=True,
                        tools=tools,
                        # response_format={
                        #     'type': 'json_object'
                        # },
                        messages=current_messages,
                    ) as completion:
                        
                        # for chunk  in completion:
                        #     print(chunk)
                        #     choice  = chunk.choices[0]
                        #     delta = choice.delta
                        #     # print(chunk)
                        #     # delta.content 是真正的 token
                        #     if delta.content:
                        #         token = delta.content
                        #         yield f"event: message\ndata: {json.dumps({'content': token})}\n\n"
                            
                        #     # 工具调用分段 (delta.tool_calls)
                        #     elif delta.tool_calls:
                        #         # 这是每次追加的一段 tool_call
                        #         # if .arguments:
                        #         print("tool_calls:------------")
                            
                                
                            # elif delta.function_call:
                            #     # 这是每次追加的一段 tool_call
                            #     pass
                            # # 完整消息（最后才会来）
                            # elif choice.finish_reason:
                            #     # finish_reason = "stop" / "tool_calls" 等
                            #     pass
                        tool_calls = {}  # index -> {id, name, arguments}
                        # for completion in llm.stream_chat_completion(messages, tools):
                        for event  in completion:
                            # print(event)
                            if event.type == "chunk":
                                snap = event.snapshot
                                if snap.choices:
                                    msg = snap.choices[0].message
                                    if msg and msg.tool_calls:
                                        for tc in msg.tool_calls:
                                            idx = tc.index
                                            tool_calls[idx] = {
                                                "id": tc.id,
                                                "name": tc.function.name,
                                                "arguments": ""   # 等待流式拼接
                                            }            
                            if event.type == "message":
                                assistant_message += event.message.content
                                round_text_buffer += event.message.content
                                # 完整消息一次性输出（可改为逐段输出）
                                yield event.message.content
                            elif event.type == "content.delta":
                                assistant_message += event.delta
                                round_text_buffer += event.delta
                                # 模型输出的每一小段（类似 ChatGPT 打字机效果）
                                # yield event.delta
                                yield f"event: message\ndata: {json.dumps({'content': event.delta})}\n\n"
                            elif event.type == "tool_calls.function.arguments.delta":
                                pass
                                # yield f"event: message\ndata: {json.dumps({'content': event.arguments_delta})}\n\n"
                            elif event.type == "tool_calls.function.arguments.done":
                                
                                # if idx in tool_calls:
                                #     # tool_calls[idx]["arguments"] = event.arguments
                                #     event.id = tool_calls[idx].id
                                pending_tool_calls.append(event)
                                print(f"Tool call {event.name}: {event.arguments}.")
                            elif event.type == "error":
                                yield f"[Error] {event.error}"
                            await asyncio.sleep(0)  # 让事件循环更流畅

                        # ---------- ② 如果没有 tool call → 完成  ----------
                        if not pending_tool_calls:
                            break
                        tool_results = []
                        if pending_tool_calls: 
                            for tc in pending_tool_calls:
                                idx = tc.index
                                if idx in  tool_calls:
                                    args = json.loads(tc.arguments)
                                    
                                    result = await self.tool_manager.run(tc.name, {"biz_id":biz_id,**args})
                                   
                                    tool_results.append({
                                        "role": "tool",
                                        "name": tc.name,
                                        "tool_call_id":  tool_calls[idx]["id"],
                                        "content": result
                                    })

                        # 将 tool 结果加入消息，继续下一轮
                           # ---------- ④ 下一轮 messages ----------
 # 1. 构造 assistant 的工具调用消息（不能带 content 文本！）
                    assistant_tool_call_msg = {
                        "role": "assistant",
                        "content": "",
                        "tool_calls": [
                            {
                                "id": tool_calls[idx]["id"],
                                "type": "function",
                                "function": {
                                    "name": tool_calls[idx]["name"],
                                    "arguments": tc.arguments,
                                },
                            }
                            for tc in pending_tool_calls
                            for idx in [tc.index]
                        ]
                    }

                    # 2. 下一轮消息
                    current_messages = (
                        current_messages
                        + [assistant_tool_call_msg]
                        + tool_results
                    )
                    # current_messages = (
                    #     current_messages
                    #     + [{"role": "assistant", "content": round_text_buffer}]
                    #     + tool_results
                    # )

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

            except Exception as e:
                print(f"Error occurred: {str(e)}")
                yield f"[Server Error] {str(e)}"

        async with BizProjectLock(biz_id, project_id):
            return StreamingResponse(
                lock_wrapper(biz_id, project_id, stream()),
                media_type="text/event-stream"
            )