from abc import ABC, abstractmethod
from nac.fpqa import FPQA

class Instruction(ABC):
    @abstractmethod
    def apply(fpqa: FPQA):
        pass

    @abstractmethod
    def verify(fpqa: FPQA) -> bool:
        pass

    @abstractmethod
    def qasm(fpqa: FPQA) -> str:
        pass

    @abstractmethod
    def avg_fidelity(fpqa: FPQA) -> float:
        pass

    @abstractmethod
    def duration(fpqa: FPQA) -> float:
        pass

    