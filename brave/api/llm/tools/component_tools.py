
async def create_script_component(arguments: dict):
    if "biz_id" not in arguments:
        return "create_script_component 缺少参数 biz_id"
    biz_id = arguments["biz_id"]
    print(arguments)
    
    return f"成创建组件脚本 for biz_id: {biz_id}"
