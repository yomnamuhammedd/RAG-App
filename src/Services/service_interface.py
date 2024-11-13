from abc import ABC,abstractmethod
from src.Helpers.config import get_settings,Settings


class ServiceInterface(ABC):
    def __init__(self):
        self.app_settings = get_settings()
    @abstractmethod
    def run(self, *args, **kwargs):
        """Executes the primary function of the service."""
        pass