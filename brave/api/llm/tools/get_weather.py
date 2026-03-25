
async def get_weather(arguments: dict):
    location = arguments.get("location")
    # 这里写你自己的逻辑
    data = f"模拟获取天气信息，位置: {location}"
    print(f"获取天气信息: {location}")
    return data