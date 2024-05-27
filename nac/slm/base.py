from abc import ABC

class SLM(ABC):
    @abstractmethod
    def toggle(self, x: int, y: int):
        pass