
from typing import Tuple
import attrs
from attr import dataclass, Factory

TRANSPARENT_COLOR = (54, 247, 87)

@attrs.define(frozen=True)  # Class is frozen to ensure that a changed value is announced
class Position:
    """Tile position of an entity."""
    x: int
    y: int
    z: int

@attrs.define(frozen=True)
class MapChunkPosition:
    """Map chunk index of an entity."""
    x: int
    y: int
    z: int
 
class Component(object):
    pass

 
class Is_Player(Component):
    pass



class Planned_Actions(Component):

    def __init__(self,data):
        self.data=data

class Movement_Dir:#TODO
    vector: str = "nullmovedir"


class Wish_Dir:
    def __init__(self, dir:str):
        self.dir: str = dir


class Terrain:
    pass

class BlocksSight:
    pass

class In_Overworld:
    pass

class Wall:
    pass

class Floor:
    pass

class FOV_Lighter:
    pass

class Health(Component):
    
    def __init__(self, current_health: int, max_health: int):
        self.current_health: int = current_health
        self.max_health = max_health



@attrs.define(frozen=True)
class My_World_Data:
    """Map chunk index of an entity."""
    current_tick : int



@attrs.define(frozen=True)
class Gravitational:
    pass

class Renderable(Component):
    def __init__(self, char: str, color: Tuple[int, int, int] = [0,0,0], bgcolor: Tuple[int, int, int] = TRANSPARENT_COLOR, prior: int = 1):
        self.char: str = char
        self.color: Tuple[int, int, int] = color
        self.bgcolor: Tuple[int, int, int] = bgcolor
        self.priority: int = prior

class Collideable(Component):
    pass
