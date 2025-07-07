# shared 模型处理器
from brave.api.service.components.base import ComponentHandler


class SharedComponentHandler(ComponentHandler):
    def create_files(self, component_data):
        print(f"[Shared] 创建公共组件文件: {component_data}")

    def get_files(self, component_data):
        print(f"[Shared] 获取公共组件文件: {component_data}")

    def update_files(self, component_data):
        print(f"[Shared] 更新公共组件文件: {component_data}")

    def delete_files(self, component_data):
        print(f"[Shared] 删除公共组件文件: {component_data}")