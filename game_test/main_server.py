import eventlet
import socketio
import random
import pickle
from components import *
from component_sets import *
import tcod.ecs
import tcod.ecs.callbacks
from worldgen import gen_world
import time

from processors import *

CHUNK_SIZE = 32

class MainServer(socketio.Namespace):

    
    game_world = tcod.ecs.World() 
    sid_entity_map = dict() #maps sids to the entity
    sid_uid_map = dict() #maps sids to the entity id

    delegator_instance = DelegatorProcessor()
    movement_instance = MovementProcessor()
    gravity_instance = GravityProcessor()
    times_connected = 0 #total amount of times people have connected to the server
    entity_counter = 10000
    real_connected_counter = 0

    tick_count = 0
    world_archive = dict()


    def on_connect(self, sid, environ):
        print('connect ', sid)
        self.times_connected += 1
        self.real_connected_counter +=1

        
       # comps = character_components(x=random.randint(20,30),y=random.randint(20,30))


        self.sid_entity_map[sid] = self.spawn_entity(component_set=character_components,x=random.randint(60,60),y=random.randint(60,60),z=15)
        self.sid_uid_map[sid] = self.entity_counter 


    def spawn_entity(self, component_set, x:int, y:int, z:int):
        self.entity_counter += 1
        ent = tcod.ecs.Entity(self.game_world,self.entity_counter)
        ent.components[Position] = Position(x=x,y=y,z=z)
        ent.components[MapChunkPosition] = MapChunkPosition(x // CHUNK_SIZE , y // CHUNK_SIZE, z // CHUNK_SIZE)

        comps = component_set()

        for comp in comps:
            ent.components[comp]=comps[comp]

        return ent

    def world_data_entity(self):

        ent = tcod.ecs.Entity(self.game_world,0)
        ent.components[My_World_Data]= My_World_Data(current_tick=self.tick_count)




    def on_meow(self,sid,data):
        print('MEOW MEOW MEOW MEWO MEOWEMWOEMWOEMWOEMWOEMWOEMWOEMWOEMWMEOWEMOWEMOWEMOWMO')

    def on_ping(self,sid,data):
        print('POING PONG PONG PONG')


    def on_print(self,sid,data):
        print(data)



    def on_disconnect(self, sid):
        print('disconnect ', sid)
        self.real_connected_counter -=1
   
        self.sid_entity_map.pop(sid)


    def on_myaction(self, sid,data) -> None:
  #      print('my action is ', data)
       

        pos = self.sid_entity_map[sid].components[Position]
        print('my location is ', pos.x, pos.y, pos.z)
   #     print('entity counter is   ',self.game_world.entity_counter)

        self.sid_entity_map[sid].components[Planned_Actions]= Planned_Actions(data)


    def process_all(self):

        start_time = time.time()

        self.delegator_instance.process(self.game_world)
        self.gravity_instance.process(self.game_world)
        self.movement_instance.process(self.game_world)

        end_time = time.time()
        elapsed = end_time - start_time
        print("Elapsed time:", elapsed, "seconds")




        #TCOD ECS CALLBACKS THANK YOU HEXDECIMAL

    @tcod.ecs.callbacks.register_component_changed(component=Position)
    def on_position_changed(entity: tcod.ecs.Entity, old: Position | None, new: Position | None) -> None:
            """Track the Position component as a tag in entities. Update the map chunk position."""
            if old == new:
                return  # Reduce cache invalidation by not adding and removing the same tag
            if old is not None:
                entity.tags.remove(old)
            if new is not None:
                entity.tags.add(new)
                entity.components[MapChunkPosition] = MapChunkPosition(new.x // CHUNK_SIZE , new.y // CHUNK_SIZE, new.z // CHUNK_SIZE)
                print("POSITION TOTALLY CHANGED IN ECS CALLBACK")
            else:  # new is None
                del entity.components[MapChunkPosition]

    @tcod.ecs.callbacks.register_component_changed(component=MapChunkPosition)
    def on_chunk_position_changed(entity: tcod.ecs.Entity, old: MapChunkPosition | None, new: MapChunkPosition | None) -> None:
            """Track the MapChunkPosition component as a tag in entities."""
            if old == new:
                return
            if old is not None:
                entity.tags.remove(old)
            if new is not None:
                entity.tags.add(new)
                print("MAP CHUNK TOTALLY CHANGED IN ECS CALLBACK")



        #TCOD ECS CALLBACKS

        




class True_Server():

    def __init__(self,online:int, port:int):



        self.server_sio = socketio.Server()
        self.app = socketio.WSGIApp(self.server_sio, static_files={
            '/': {'content_type': 'text/html', 'filename': 'index.html'}
        })
        self.ms  = MainServer('/')
        

        self.online = online #0 = single player, #1= hosting, #2 = connecting
        self.port = port
        


        self.server_sio.register_namespace(self.ms)

    def server_listen(self):
        eventlet.spawn(eventlet.wsgi.server(eventlet.listen(('', self.port)), self.app))


    def send_entities(self):
        
        pickled_data: bytes = pickle.dumps(self.ms.game_world)
        self.server_sio.emit("array_full",pickled_data)
        

        for sid in self.ms.sid_uid_map:
            pickled_local_id : bytes = pickle.dumps(self.ms.sid_uid_map[sid])
            self.server_sio.emit('receive_own_id', data=pickled_local_id, room=sid)
            print("SENT OUT ",self.ms.sid_uid_map[sid])


        

    #    print('EMITTED  ', frozen)

    def send_planned_actions(self):

  


        eid_pa_dict = dict() # dictionary of eid keys and planned_actions values
        eid_pa_dict[0]= self.ms.tick_count

        for ent, actions in self.ms.game_world.Q[tcod.ecs.Entity,Planned_Actions]:

            print('eid is ', ent.uid)

            act_data = actions.data

            

            eid_pa_dict[ent.uid]= act_data


        pickled_data: bytes = pickle.dumps(eid_pa_dict)
        self.server_sio.emit("planned_actions",pickled_data)

    def game_loop(self):

        connected_counter = 0
        
        
        while True:

            self.ms.tick_count += 1
            self.ms.world_data_entity()

            if self.ms.times_connected != connected_counter:
                print("hai")

                self.send_entities()
                self.ms.process_all()

            elif connected_counter!= 0 :     
                print("hai")

                self.send_planned_actions()
                self.ms.process_all()
         

            connected_counter = self.ms.times_connected    
            eventlet.sleep(.1)

    def spawn_game_loop(self):
        eventlet.spawn(self.game_loop)

    def start_everything(self):
      #      self.ms.server_call_backs()
            gen_world(self.ms)
            self.spawn_game_loop()
            self.server_listen()
            
            




if __name__ == '__main__':
    meow_server = True_Server(0,5000)

    eventlet.spawn(meow_server.start_everything())