import os

from flask import json
from brave.api.enum.component_script import ScriptName
from brave.api.llm.schemas.llm import ChatRequest
from brave.api.schemas.chat_history import CreateChatHistory
from brave.api.service import analysis_service, chat_history_service
from brave.api.service import analysis_result_service
import brave.api.service.pipeline as  pipeline_service
from brave.api.config.db import get_engine


async def build_prompt(req: ChatRequest, system_prompt: str, template: str,queue) -> str:
    async def emit(msg):
        if queue:
            await queue.put(msg)
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
                tool_name = find_relation["name"]
                await emit({"title":f"Fetch Tool Info","content":f"Fetching tool {tool_name} information..."})
                if find_relation["prompt"]:
                    context = find_relation["prompt"]
                if find_relation["content"]:
                    from_prompt = """
                    The following is a JSON form used when inputting scripts.
                    """
                    data = from_prompt+"\n"+find_relation["content"]
                
                component_script = pipeline_service.find_component_module(find_relation,ScriptName.main)['path']
                if os.path.exists(component_script):
                    with open(component_script, "r") as f:
                        code = f.read()
                    await emit({"title":f"Fetch Tool Script","content":f"Fetching tool {tool_name} script..."})

        elif biz_type=="script":
            component = pipeline_service.find_component_by_id(conn, biz_id)
            if component:
                if component["prompt"]:
                    context = component["prompt"]
                if component["content"]:
                    from_prompt = """
                    The following is a JSON form used when inputting scripts.
                    """
                    data = from_prompt+"\n"+component["content"]
                
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
                analysis_name = find_analysis["analysis_name"]
                await emit({"title":f"Fetch Analysis Info","content":f"Fetching analysis {analysis_name} information..."})
                # raise HTTPException(status_code=404, detail="Analysis not found")
                output_dir = find_analysis["output_dir"]
                prompt = f"{output_dir}/output/prompt.ai"
                if find_analysis["relation_prompt"]:
                    context = find_analysis["relation_prompt"]
                if os.path.exists(prompt):
                    prompt0 = "The analysis results are as follows:\n"
                    with open(prompt, "r") as f:
                        data =  prompt0 + f.read()
                    await emit({"title":f"Fetch Analysis Prompt","content":f"Read {analysis_name} prompt.ai file..."})
                if find_analysis["pipeline_script"]:
                    component_script = find_analysis["pipeline_script"]
                    if os.path.exists(component_script):
                        with open(component_script, "r") as f:
                            code = f.read()
                        await emit({"title":f"Fetch Analysis Script","content":f"Fetching analysis {analysis_name} script..."})

        
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