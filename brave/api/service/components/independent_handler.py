# independent 模型处理器
from brave.api.service.components.base import ComponentHandler


class IndependentComponentHandler(ComponentHandler):
    def create_files(self, component_data):
        print(f"[Independent] 创建独立组件文件: {component_data}")

    def get_files(self, component_data):
        print(f"[Independent] 获取独立组件文件: {component_data}")

    def update_files(self, component_data):
        print(f"[Independent] 更新独立组件文件: {component_data}")

    def delete_files(self, component_data):
        print(f"[Independent] 删除独立组件文件: {component_data}")