from rich.segment import Segment
from rich.style import Style

from textual.strip import Strip
from textual.widget import Widget
from textual.app import App, ComposeResult
from textual.containers import ScrollableContainer, Horizontal, Vertical, Grid
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Static, Placeholder, RichLog
from textual.scroll_view import ScrollView
from textual.binding import Binding
from textual.color import Color
from textual.message import Message
from textual import events

import time
import socketio
import eventlet
import pickle
import numpy as np
import tcod.ecs

from algos import  get_orthonormal_pair
from ndbresen import bresenhamline
from components import *
from processors import *
from component_sets import *
from worldgen import generate_hollow_rectangle

from main_server import True_Server, MainServer

 


class Game(ScrollView, can_focus=True):
    """starts game"""

    screen_height = 70
    screen_width = 100
    render_array = []
    client_sio = socketio.Client()
    
    frame_counter = reactive(0)
    local_server = MainServer()

    wish_to_be_online = 0
    local_player_id = 0
    fully_received=0

    planned_actions_dict = dict()
    my_mouse_location = None
    mouse_cursor_height = 10
    seen_terrain = set() # turn this into just an array of segments
    seen_ents = set()

    prev_cursor_tile= None

 



    BINDINGS = [
        Binding("w", "movement('up')", "Up", show=False, priority=True),
        Binding("a", "movement('left')", "Left", show=False, priority=True),
        Binding("s", "movement('down')", "Down", show=False, priority=True),
        Binding("d", "movement('right')", "Right", show=False, priority=True),
    ]


    class Updated(Message):
        """Color selected message."""

        def __init__(self, player) -> None:
            self.player = player
            
            super().__init__()



    class Randomdata(Message):
        """Color selected message."""

        def __init__(self, mousetile3d) -> None:

            self.mouse_tile_3d_loc = mousetile3d
            super().__init__()
  
    def initialize_render_array(self):

        self.screen_width = self.size.width if (self.size.width %2 == 1) else self.size.width-1
        self.screen_height = self.size.height if (self.size.height %2 == 1) else self.size.height-1

        self.render_array = [[Segment('⊕', Style(color="#ccccdb") + Style(bgcolor="#242429")) for _ in range(self.screen_width)] for _ in range(self.screen_height)]



    def update_array(self):

        self.initialize_render_array()

     
        

        if self.local_player_id > 0 and self.fully_received > 0:
            start_time = time.time()
            world = self.local_server.game_world
            half_width = self.screen_width // 2 # +1 if (self.screen_width % 2 == 0) else self.screen_width // 2 
            half_height = self.screen_height // 2  #-1 if (self.screen_height % 2 == 0) else self.screen_height // 2 



            my_character = world[self.local_player_id]
            char_pos = my_character.components[Position]
            char_rend = my_character.components[Renderable]
            char_chunk_x = my_character.components[MapChunkPosition].x
            char_chunk_y = my_character.components[MapChunkPosition].y
            char_chunk_z = my_character.components[MapChunkPosition].z

            offset_x = char_pos.x - half_width
            offset_y = char_pos.y - half_height

            log_message = self.Updated(my_character)
            

            self.post_message(log_message)

         
            terrain_union = set()
            overworld_union = set()   

            for x_off in [-2, -1, 0, 1, 2]:
                for y_off in [-2, -1, 0, 1, 2]:
                    for z_off in [-1, 0, 1]:
                        terrain_union.update(world.Q.all_of(components=[Terrain], tags=[MapChunkPosition(char_chunk_x + x_off, char_chunk_y + y_off, char_chunk_z + z_off)]))
                        overworld_union.update(world.Q.all_of(components=[In_Overworld], tags=[MapChunkPosition(char_chunk_x + x_off, char_chunk_y + y_off, char_chunk_z + z_off)]))
            priority_list = [[0] * self.screen_width for _ in range(self.screen_height)]

            def tint_color(my_z_diff, my_color):
                if my_z_diff > 0:
                    tint_factor = my_z_diff / 40
                    aR, aG, aB = 255, 255, 255
                else:
                    tint_factor = -my_z_diff / 10
                    aR, aG, aB = 0, 0, 0
                newR = my_color[0] + (aR - my_color[0]) * tint_factor
                newG = my_color[1] + (aG - my_color[1]) * tint_factor
                newB = my_color[2] + (aB - my_color[2]) * tint_factor
                newR = int(max(0, min(newR, 255)))
                newG = int(max(0, min(newG, 255)))
                newB = int(max(0, min(newB, 255)))
                return f"rgb({newR},{newG},{newB})"

            def draw_ents(ent_set_union, my_char_pos):
                for ent in ent_set_union:
                    pos = ent.components[Position]
                    rend = ent.components[Renderable]

                    
                    if (abs(pos.x - my_char_pos.x) < half_width) and (abs(pos.y - my_char_pos.y) < half_height):
                        z_diff = my_char_pos.z - pos.z
                        rgb = rend.color
                        bgrgb = rend.bgcolor
                        front_color = tint_color(z_diff, rgb)
                        back_color = tint_color(z_diff, bgrgb)
                        ent_char = rend.char
                        render_x = pos.x - offset_x
                        render_y = pos.y - offset_y
                        true_prio = (pos.z * 10) + rend.priority
                        if priority_list[render_y][render_x] < true_prio:
                            priority_list[render_y][render_x] = true_prio
                            final_style = ""
                            if bgrgb == TRANSPARENT_COLOR:
                                bgtouse = self.render_array[render_y][render_x].style.bgcolor
                                final_style = Style.parse(front_color) + Style(bgcolor=bgtouse)
                            else:
                                final_style = Style.parse(front_color) + Style(bgcolor=back_color)
                            self.render_array[render_y][render_x] = Segment(ent_char, final_style)

            visible_terrain = set()
            visible_ents = set()
            visible_points = []



            def shadowcast_to_mouse():


                    if (self.my_mouse_location is not None):
                        mouse_char_offset_x = self.my_mouse_location[0] - half_width
                        mouse_char_offset_y = self.my_mouse_location[1] - half_height

                        at_mouse_top_z = 0
                        
                        for zdeep in range(20):
                            someth = char_pos.z + self.mouse_cursor_height - zdeep
                            if check_collision(world, char_pos.x+mouse_char_offset_x,char_pos.y-mouse_char_offset_y,someth)[0]:
                                pass
                            else:
                                at_mouse_top_z = someth
                                break
                    
                                
                        char_pos_array = np.array([[char_pos.x,char_pos.y,char_pos.z]])
                        char_look_array = np.array([[char_pos.x+mouse_char_offset_x,char_pos.y-mouse_char_offset_y,at_mouse_top_z]])
                    
                        all_points = bresenhamline(char_pos_array, char_look_array, max_iter=-1)

                  
                   
                        my_len = len(all_points) - 1
                        
                        initial_point = np.array(all_points[0])
                        initial_goal_point = np.array(all_points[my_len])
                        look_vector = initial_goal_point - initial_point
                        x_ortho, y_ortho = get_orthonormal_pair(look_vector)
                        
                        def add_ent_to_sight_set(ent,my_set,holder_set):
                            if self.my_mouse_location == self.prev_cursor_tile:
                                holder_set.add(ent)
                            else:
                                holder_set.clear()
                                holder_set.add(ent)
                                self.prev_cursor_tile=self.my_mouse_location



                        def march_and_collect(bren_line):
                            
                            for point in bren_line:
                                    cbs = check_block_sight(world, point[0],point[1],point[2])
                                    cc = check_collision(world, point[0],point[1],point[2])
                                    cf = check_floor(world, point[0],point[1],point[2])
                                    if cbs[0]:
                                        visible_points.append(point)
                                    if not cf[0]:
                                        visible_points.append(point)
                                        add_ent_to_sight_set(cf[1],visible_terrain,self.seen_terrain)


                                    if not cc[0]:
                                        visible_points.append(point)
                                        visible_ents.add(cc[1])    
                                        add_ent_to_sight_set(cc[1],visible_ents,self.seen_ents)
                                    if not cbs[0]:
                                        visible_points.append(point)
                                        add_ent_to_sight_set(cbs[1],visible_terrain,self.seen_terrain)

                                        break


                        line_counter = 1000
                        point_list = []
                        max_depth = len(all_points) // 2
                        if max_depth >6: max_depth =6
                        
                        for dep in range(max_depth):

 
                          #      self.client_sio.emit("print", "INSIDE DEP LOOP")
                                
                                beep = dep + 1
                                viewport_scale = 2
                                viewport_size = viewport_scale*2*beep
                                #currec = generate_hollow_rectangle(2*beep,2*beep,(-beep,-beep,0))
                                viewport_coord = viewport_scale*(-beep)
                                currec = generate_hollow_rectangle(viewport_size,viewport_size,(viewport_coord,viewport_coord,0))
                                new_goal_points = []
                               # modded_start = all_points[beep]
                            #    self.client_sio.emit("print", "MAMA MIA MAMA MIA MAMA MIA")
                   
                                for point in currec:
                                    modded_goal = initial_goal_point + point[0]*x_ortho + point[1]*y_ortho
                                    modded_goal = modded_goal.astype(int)
                                    new_goal_points.append(modded_goal)
                                
                                for point in new_goal_points:
                                    mys = char_pos_array if dep == 0 else np.array([all_points[dep]])
                                  #  mys = np.array([all_points[dep]])
                                    mye = np.array([modded_goal])
                                    mod_bren = bresenhamline(mys,mye, max_iter=-1)
                                    march_and_collect(mod_bren)

                       # self.seen_terrain = self.seen_terrain.union(visible_terrain)

             
                    else:
                        return []

                
                         


          #  shadowcast_to_mouse()

            
            draw_ents(terrain_union, char_pos)
            draw_ents(overworld_union, char_pos)
            #draw_ents(self.seen_terrain, char_pos)
           # draw_ents(self.seen_ents, char_pos)
          #  light_ents(light_list,char_pos)
            
            end_time = time.time()
            elapse = end_time - start_time
           # self.client_sio.emit("print", "RENDER ELAPSED TIME IS")
          #  self.client_sio.emit("print", elapse)
          #  self.client_sio.emit("print", "VISIBLE TILES LENGTH")
          #  self.client_sio.emit("print", len(visible_points))


         

         #   print('UPDATE ARRAY  ', self.render_array)

    def action_movement(self, dir: str) -> None:
        self.client_sio.emit('myaction',[['move', dir]])

    def on_mouse_move(self, event: events.MouseMove) -> None:

        

        self.my_mouse_location = (event.x,event.y)
        self.frame_counter+=1

    def on_game_resize(self):
        self.update_array()



    def call_backs(self):

            @self.client_sio.on('array_full')
            def on_array_full(data):
 
                thawed = pickle.loads(data)
                self.local_server.game_world = thawed
                self.fully_received+=1

                
                self.frame_counter+=1

            @self.client_sio.on('receive_own_id')
            def on_receive_own_id(data):
 
                thawed = pickle.loads(data)
                self.local_player_id = int(thawed)
            #    self.client_sio.emit("print","MY ID IS ")
            #    self.client_sio.emit("print",self.local_player_id)

                self.frame_counter+=1



            @self.client_sio.on('planned_actions')
            def on_planned_actions(data):

                    thawed = pickle.loads(data)


                    for x in thawed:
                      if x != 0:  

                        #self.planned_actions_dict[this_tick].append((x,thawed[x] ))

                            my_data = thawed[x]
                            ent = self.local_server.game_world[x]
                            ent.components[Planned_Actions]= Planned_Actions(my_data)

                        
                    self.local_server.process_all() #I AM STUCK EHRE NMUST DO MAIN SERVER
                    self.frame_counter+=1
                    



    def on_mount(self):
 
        self.client_sio.connect('http://localhost:5000')
        self.client_sio.emit("meow","meow")
        self.client_sio.emit("meow","meow")

        self.call_backs()
        self.update_array()
        




    def render_line(self, y: int) -> Strip:
        """Render a line of the widget. y is relative to the top of the widget."""

        if y == 0: self.update_array()
        if y > self.screen_height -1:
            # Generate a blank line when we reach the end
            return Strip.blank(self.size.width)

        true_y = self.screen_height -1 - y

        strip = Strip(self.render_array[true_y], self.screen_width)

        return strip


class GameContainer(Grid):

    last_game_message = None
    last_mouse_message = None
    last_random_message = None

    def compose(self) -> ComposeResult:
        yield Game(id="game1")
        yield RichLog(id="log1")

    def on_mount(self) -> None:
        log = self.query_one(RichLog)
        game = self.query_one(Game)
        sh = game.screen_height
        log.write("Health: 50")
        log.write(sh)

    def write_stats(self) -> None:

        game_message = self.last_game_message
        mouse_message = self.last_mouse_message
        random_message = self.last_random_message
        
        log = self.query_one(RichLog)
        game = self.query_one(Game)
        log.clear()

        if game_message is not None:
            pos_x = game_message.player.components[Position].x
            pos_y = game_message.player.components[Position].y
            pos_z = game_message.player.components[Position].z
            player_health = game_message.player.components[Health].current_health
            player_max_health = game_message.player.components[Health].max_health

            hea_str = f"Health: {player_health} / {player_max_health}"
            pos_str = f"XYZ: {pos_x} , {pos_y} , {pos_z}"
            log.write(hea_str)
            log.write(pos_str)

            if game.my_mouse_location is not None:
                mouse_x = game.my_mouse_location[0]
                mouse_y = game.my_mouse_location[1]
                mouse_str = f"Mouse:( {mouse_x} , {mouse_y} )"
                log.write(mouse_str)

        if random_message is not None:
            mt = random_message.mouse_tile_3d_loc
            
            random_str = f"random:( {mt[0]} , {mt[1]}, {mt[2]} )"
            log.write(random_str)
  

    def on_game_updated(self, game_message: Game.Updated) -> None:
        self.last_game_message = game_message
        self.write_stats()
        


    def on_game_randomdata(self, data_message: Game.Randomdata) -> None:
        self.last_random_message = data_message
        self.write_stats()
        



        


class GameScreen(Screen):
    def compose(self) -> ComposeResult:
        yield GameContainer()








class GameApp(App):
    """A simple app to show our widget."""
    def on_ready(self) -> None:
        self.push_screen(GameScreen())
    







if __name__ == "__main__":
    time.sleep(1)
    app = GameApp(css_path="game.tcss")
    app.run()
