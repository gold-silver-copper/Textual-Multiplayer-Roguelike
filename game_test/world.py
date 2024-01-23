from entity import Entity
from components import *
from component_sets import *


class World(object):
    """
    A generic object to represent players, enemies, items, etc.
    """
    def __init__(self):
            self.entities = dict()
            self.entity_counter = 0 #  entitity ids start at this number
            self.game_tick = 0

            #entity indexer is a dict with keys being component names, and values being lists of entities who possess those components
            self.entity_indexer = dict()

 

    def spawn_entity(self, component_set, x:int,y:int) -> int:

        id_to_use = self.entity_counter
        self.entity_counter += 1

        set_to_add = component_set(id=id_to_use,x=x,y=y)        
        self.entities[id_to_use] = Entity(set_to_add)

        for comp in set_to_add:
            self.entity_indexer[comp_to_str(comp)].add(id_to_use)

        print("ENITY INDEXER IS   ", self.entity_indexer)

        

        return id_to_use
        
    def delete_entity(self,eid:int):
        if eid in self.entities:

            for key in self.entities[eid].components:
                self.entity_indexer[key].remove(eid)


            self.entities.pop(eid)
#NEVER FORGET ABOUT THE INDEXER IT WILL HAUNT YOU
    def add_component(self, eid :int, component):

        comp_str = comp_to_str(component)

        if eid not in self.entity_indexer[comp_str]:

            self.entities[eid].components[comp_str] = component
            self.entity_indexer[comp_str].add(eid)

            #ADD INDEXER STUFF
    
    def delete_component(self,eid:int, comp_str:str):



        if eid in self.entity_indexer[comp_str]:
            self.entities[eid].components.pop(comp_str)

   
            self.entity_indexer[comp_str].discard(eid)
              



    def run_planned_actions(self):

        for eid in self.entity_indexer["planned_actions"]:

            
                if self.entities[eid].components["planned_actions"]:

                    act_data = self.entities[eid].components["planned_actions"].data

                
                    for act in act_data:
                        if act[0]=='move':  
                            self.move_entity(eid=eid,dir=act[1])             

                    self.entities[eid].components["planned_actions"].data = []


    def move_entity(self,eid:int,dir:str):



                cur_x = self.entities[eid].components["position"].x
                cur_y = self.entities[eid].components["position"].y



                if dir == 'up':
                    cur_x+=0
                    cur_y+=1
                if dir == 'down':
                    cur_x+=0
                    cur_y+=-1
                if dir == 'left':
                    cur_x+=-1
                    cur_y+=0
                if dir == 'right':
                    cur_x+=1
                    cur_y+=0

                if self.check_collision(wish_x=cur_x,wish_y=cur_y):
                    self.entities[eid].components["position"].x =cur_x
                    self.entities[eid].components["position"].y =cur_y

            
    def check_collision(self,wish_x:int,wish_y:int):

        for eid in self.entity_indexer["collideable"]:
            coll = False
            my_x = False
            my_y = False
    

            if self.entities[eid].components["collideable"]:
                    coll = self.entities[eid].components["collideable"].collide
            if self.entities[eid].components["position"]:
                    my_x = self.entities[eid].components["position"].x
                    my_y = self.entities[eid].components["position"].y


                


            if coll and (my_x == wish_x) and (my_y== wish_y) :
                        return False

        return True




    def initialize_entity_indexer(self):

        wee = every_components()

        for comp in wee:
            self.entity_indexer[comp_to_str(comp)] = set()


    def initialize_world(self):
        self.initialize_entity_indexer()



    
            
            

