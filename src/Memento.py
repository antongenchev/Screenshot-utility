from src.utils import Box

class Memento:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            self.__setattr__(key, value)
    
