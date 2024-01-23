import pickle
from components import *
from component_sets import *
import tcod.ecs
#from worldgen import gen_world

from processors import *


world = tcod.ecs.World()
ent = world.new_entity()
ent.components[Position] = Position(x=random.randint(20,30),y=random.randint(20,30))
ent.components[Renderable] = Renderable( "@", (255, 255, 255))
ent.components[Int_ID] = Int_ID(self.entity_counter)

uid_data_dict = dict() # dictionary of uid keys and planned_actions values

for ent, actions in self.ms.game_world.Q[tcod.ecs.Entity,Planned_Actions]:

            act_data = actions.data

            if act_data != []:


                uid_data_dict[ent.uid]= act_data

        pickled_data: bytes = pickle.dumps(eid_pa_dict)
        self.sio.emit("planned_actions",pickled_data)

print(my_world)



