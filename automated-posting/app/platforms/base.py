from abc import ABC, abstractmethod
from app.schemas import PlatformResult

class BasePlatform(ABC):
    name: str

    @abstractmethod
    async def publish(self, message: str) -> PlatformResult:
        raise NotImplementedError
