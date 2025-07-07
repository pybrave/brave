from brave.api.service.components.base import ComponentHandler
from brave.api.service.components.shared_handler import SharedComponentHandler
from brave.api.service.components.independent_handler import IndependentComponentHandler


class ComponentHandlerFactory:
    @staticmethod
    def get_handler(component_model: str) -> ComponentHandler:
        if component_model == "shared":
            return SharedComponentHandler()
        elif component_model == "independent":
            return IndependentComponentHandler()
        else:
            raise ValueError(f"未知组件模型: {component_model}")
