import time
from typing import Any, Optional, Dict
from src.utils import Box
from src.config import config

class Memento:
    def __init__(self,  _source:Optional[str]=None, **kwargs,):
        # Store the data
        for key, value in kwargs.items():
            if key.startswith('_'):
                raise Exception(f'Not allowed for keys to start with an underscored: {key}')
            setattr(self, key, value)

        # Save the timestamp of when the memento was created
        self._timestamp_created = time.time()

        self._source = _source # indicate the source of the memento creation

    def is_related(self, m:'Memento') -> bool:
        '''
        Check if the memento m is related to the current memento.
        This function can be overriden in more concrete implementations of Mementos

        Parameters:
            m: the other memento object to compare with
        Returns:
            (bool) whether the two mementos are considered related
        '''
        return False

