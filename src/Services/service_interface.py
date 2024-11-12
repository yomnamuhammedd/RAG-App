from abc import ABC,abstractmethod


class ServiceInterface(ABC):
    @abstractmethod
    def run(self, *args, **kwargs):
        """Executes the primary function of the service."""
        pass