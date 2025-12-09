from abc import ABC, abstractmethod

class MemoryProtocol(ABC):
    
    @abstractmethod
    def add_interaction():
        pass

    @abstractmethod
    def to_json():
        pass

