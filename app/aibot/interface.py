# 2024/5/8
# zhangzhong
# AIBot interface

from abc import ABC, abstractmethod
from typing import AsyncGenerator

from app.common.model import ChatMessage


# ABC全称是Abstract Base Class，提供了一个基础类，用于定义抽象基类
class AIBot(ABC):
    # abstractmethod 标记了方法必须由子类实现
    @abstractmethod
    # AsyncGenerator[ChatMessage, None] 中的None表示调用者无法向生成器发送值
    async def ainvoke(self, input: ChatMessage) -> AsyncGenerator[ChatMessage, None]:
        pass
