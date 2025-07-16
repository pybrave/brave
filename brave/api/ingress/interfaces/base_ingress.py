
import abc

class BaseMessageIngress(abc.ABC):
    @abc.abstractmethod
    async def start(self):
        """启动消息监听器"""
        pass