from src.Memento import Memento
from src.config import config

class Caretaker():
    def __init__(self):
        self._mementos = {} # obj_id -> list of mementos
        self._idx = {} # obj_id -> index of current memento
        self._max_mementos = {} # obj_id -> the maximum number of mementos to be stored

    def save(self, obj_id, memento:Memento):
        '''
        Save the memento and append it to the history. Update the current index

        Parameters:
            obj_id: the name/id of the object for which the mementos are stored
            memento: the Memento object
        '''
        if obj_id not in self._mementos:
            self._mementos[obj_id] = []
            self._idx[obj_id] = -1
            self._max_mementos[obj_id] = config['mementos']['max_num_mementos']
        # Remove any mementos after the current index (in case of undone steps)
        if len(self._mementos[obj_id]) > 0 and self._idx[obj_id] < len(self._mementos[obj_id]) - 1:
            self._mementos[obj_id] = self._mementos[obj_id][:self._idx[obj_id] + 1]
        # Append the new memento
        self._mementos[obj_id].append(memento)
        # Check if the number of mementos exceeds the maximum limit
        if len(self._mementos[obj_id]) > self._max_mementos[obj_id]:
            # Remove the oldest memento
            self._mementos[obj_id].pop(0)
        # Updae the current index to point to the last memento
        self._idx[obj_id] = len(self._mementos[obj_id]) - 1

    def undo(self, obj_id:str):
        '''
        Undo - load one memento back in the history if there is a such one

        Parameters:
            obj_id: the name/id of the object for which the mementos are stored
        '''
        if obj_id not in self._mementos:
            return None
        # Set the new current index if it is valid
        if self._idx[obj_id] - 1 < 0:
            return None
        self._idx[obj_id] -= 1
        # Return the current memento object
        return self._mementos[obj_id][self._idx[obj_id]]

    def redo(self, obj_id:str):
        '''
        Redo - load one memento ahead in the history if there is a such one

        Parameters:
            obj_id: the name/id of the object for which the mementos are stored
        '''
        if obj_id not in self._mementos:
            return None
        # Set the new current index if it is valid
        if self._idx[obj_id] + 1 >= len(self._mementos[obj_id]):
            return None
        self._idx[obj_id] += 1
        # Return the current memento object
        return self._mementos[obj_id][self._idx[obj_id]]

caretaker = Caretaker()