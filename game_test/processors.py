import tcod.ecs
from components import *


def check_collision(world,wish_x:int,wish_y:int,wish_z:int):

        for ent in world.Q.all_of(components=[Collideable],tags=[Position(wish_x, wish_y,wish_z)]):
                return (False,ent) # Does collide with wish direction


        return (True,None) # Does not collide



def check_floor(world,cur_x:int,cur_y:int,cur_z:int):

        for ent in world.Q.all_of(components=[Floor],tags=[Position(cur_x, cur_y,cur_z)]):
                return (False,ent) # Has floor on given tile


        return (True,None) # Does not collide


def check_block_sight(world,wish_x:int,wish_y:int,wish_z:int):

        for ent in world.Q.all_of(components=[BlocksSight],tags=[Position(wish_x, wish_y,wish_z)]):
                return (False,ent) # Tile blocks vision

        return (True,None) # Does not collide



class DelegatorProcessor:

    def process(self, world):

        for ent, actions in world.Q[tcod.ecs.Entity,Planned_Actions]:

                    act_data = actions.data

                
                    for act in act_data:
                        if act[0]=='move': 
                            ent.components[Wish_Dir] =  Wish_Dir(act[1])
                            
    

                    del ent.components[Planned_Actions]


class MovementProcessor:
    def process(self,world):

        for ent, wdir, pos in world.Q[tcod.ecs.Entity,Wish_Dir,Position]:

                cur_x = pos.x
                cur_y = pos.y
                cur_z = pos.z

                dir = wdir.dir
                del ent.components[Wish_Dir]



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

                if dir == 'jump':
                    cur_z+=1
                    #and standing on ground
                    
                front_col = check_collision(world=world,wish_x=cur_x,wish_y=cur_y, wish_z=cur_z)[0]
                front_up_col = check_collision(world=world,wish_x=cur_x,wish_y=cur_y, wish_z=cur_z+1)[0]

        
                if (cur_x>0 and cur_y>0 and cur_z>0)  and front_col:
                    ent.components[Position] = Position(x=cur_x,y=cur_y,z=cur_z)
                elif (cur_x>0 and cur_y>0 and cur_z>0)  and front_up_col and not front_col:
                    ent.components[Position] = Position(x=cur_x,y=cur_y,z=cur_z+1)
       

            

#TURN THIS INTO MOMENTUM PROCESSOR
class GravityProcessor:
    def process(self,world):
        for e in world.Q.all_of(components=[Gravitational]):

            pos = e.components[Position] 

            cur_x = pos.x
            cur_y = pos.y
            cur_z = pos.z - 1
            cf = check_floor(world,pos.x,pos.y,pos.z)
            print(cur_x)
            print(cf[0])

            if (cur_x>0 and cur_y>0 and cur_z>0) and cf[0] and check_collision(world=world,wish_x=cur_x,wish_y=cur_y, wish_z=cur_z)[0]:
                e.components[Position] = Position(x=cur_x,y=cur_y,z=cur_z)




    
            