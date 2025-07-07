# 抽象基类
class ComponentHandler:
    def create_files(self, component_data):
        raise NotImplementedError
    def update_files(self, component_data):
        raise NotImplementedError
    def delete_files(self, component_data):
        raise NotImplementedError
    def get_files(self, component_data):
        raise NotImplementedError

    
