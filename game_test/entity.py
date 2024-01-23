from typing import Tuple
from components import *

class Entity(object):
    """
    A generic object to represent players, enemies, items, etc.
    """
    def __init__(self, components : set):
        self.components = dict()

        for component in components:
            self.components[comp_to_str(component)] = component

 