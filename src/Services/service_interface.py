from abc import ABC,abstractmethod
from src.Helpers.config import get_settings,Settings
from asyncinit import asyncinit
@asyncinit
class ServiceInterface(ABC):
    async def __init__(self):
        self.app_settings = get_settings()
        
    @abstractmethod
    async def run(self, *args, **kwargs):
        """Executes the primary function of the service."""
        pass