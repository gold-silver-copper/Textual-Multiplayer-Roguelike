#from entity import Entity
from components import *
from component_sets import *
#from main_server import MainServer
import tcod.bsp
import numpy as np


def generate_rectangle(width, height, starting_corner):
    x, y, z = starting_corner
    if width <= 0 or height <= 0 or z < 0:
        return []
 
    # Calculate the coordinates for the opposite corner
    opposite_corner = (x + width, y + height, z)

    # Generate the list of coordinates for the rectangle
    rectangle_coordinates = []
    for i in range(x, opposite_corner[0]):
        for j in range(y, opposite_corner[1]):
            rectangle_coordinates.append((i, j,z))

    return rectangle_coordinates

def generate_hollow_rectangle(width, height, starting_corner):
    x, y, z = starting_corner
    if width <= 0 or height <= 0 or z < 0:
        return []

    # Calculate the coordinates for the opposite corner
    opposite_corner = (x + width, y + height, z)

    # Generate the list of coordinates for the rectangle with a hollow center
    rectangle_coordinates = []
    for i in range(x, opposite_corner[0]):
        for j in range(y, opposite_corner[1]):
            if i == x or i == opposite_corner[0] - 1 or j == y or j == opposite_corner[1] - 1:
                rectangle_coordinates.append((i, j,z))

    return rectangle_coordinates

def generate_house(world, width, height, starting_corner, wall_material,door_material,furniture_group):
        rect_coords = generate_hollow_rectangle(width, height, starting_corner)
      
        up_coords = generate_hollow_rectangle(width, height, starting_corner)
        corn_x,corn_y, corn_z = starting_corner
        inner_corner = (corn_x+1,corn_y+1,corn_z)
        inner_coords = generate_hollow_rectangle(width-2, height-2, inner_corner)
        furniture = furniture_group()

        door_place = random.randint(1,2*(width+height)-2)
        


        for x,y,z in up_coords:

                world.spawn_entity(wall_material,x,y,z+1)
                world.spawn_entity(wall_material,x,y,z+2)
            #    world.spawn_entity(wall_material,x,y,z+3)
            #    world.spawn_entity(wall_material,x,y,z+4)

        for x,y,z in rect_coords:
            if door_place==0:
                door_place-=1
                world.spawn_entity(door_material,x,y,z)
                world.spawn_entity(door_sign,x,y,z+1)
                world.spawn_entity(door_sign,x,y,z+2)
                world.spawn_entity(door_sign,x,y,z+3)

            else:
                door_place-=1
                world.spawn_entity(wall_material,x,y,z)

        for x,y,z in inner_coords:
            if 5==random.randint(1,10):
                
                world.spawn_entity(random.choice(tuple(furniture)),x,y,z)

           

def generate_town(world,width,height,town_start_corner,style):

        if style == 'common_egyptian':
            wallm=sandstone_wall
            doorm=sandstone_passage
            furn=egyptian_common_furniture

        corn_z = town_start_corner[2]

        bsp = tcod.bsp.BSP(x=town_start_corner[0], y=town_start_corner[1], width=width, height=height)
        bsp.split_recursive(
            depth=5,
            min_width=5,
            min_height=5,
            max_horizontal_ratio=3,
            max_vertical_ratio=3,
        )

        # In pre order, leaf nodes are visited before the nodes that connect them.
        for node in bsp.pre_order():
            if node.children:
                node1, node2 = node.children
                print('Connect the rooms:\n%s\n%s' % (node1, node2))
            else:
                print('Dig a room for %s.' % node)
                generate_house(world,node.width-2,node.height-2,(node.x,node.y,corn_z),wallm,doorm,furn)


def generate_physical_terrain(world,width,height):

    noise = tcod.noise.Noise(

    dimensions=2,

    algorithm=tcod.noise.Algorithm.SIMPLEX,

    seed=42002,)


    z = 1

    samples = noise[tcod.noise.grid(shape=(width, height), scale=0.25, origin=(0, 0))]
    samples = ((samples + 1.0) * (256 / 2)).astype(np.uint8)


    for i in range(len(samples)):
        for j in range(len(samples[i])):
            meowb = samples[i][j] // 30

            if 90<=samples[i][j] <= 100:
           
                world.spawn_entity(sandstone_wall,i,j,1)
                world.spawn_entity(sandstone_wall,i,j,0)
            if 100<samples[i][j] <= 130:
           
                world.spawn_entity(sandstone_wall,i,j,2)
                world.spawn_entity(sandstone_wall,i,j,1)
            if 130<samples[i][j] <= 160:
           
                world.spawn_entity(sandstone_wall,i,j,3)
                world.spawn_entity(sandstone_wall,i,j,2)
            if 160<samples[i][j] <= 200:
           
                world.spawn_entity(sandstone_wall,i,j,4)
                world.spawn_entity(sandstone_wall,i,j,3)
            if 200 <samples[i][j]:
           
                world.spawn_entity(sandstone_wall,i,j,5)
                world.spawn_entity(sandstone_wall,i,j,4)
     


def fill_ground(world,width,height):
    for i in range(width):
        for j in range(height):
           # world.spawn_entity(dirt_block,i,j,1)
            world.spawn_entity(dirt_block,i,j,0)



def gen_world(world):


      
        fill_ground(world,300,300)
        #generate_physical_terrain(world,100,100)

        generate_town(world,100,100,(0,0,1),'common_egyptian')
        world.spawn_entity(npc_components, x=30,y=30,z=5)
      #  self.spawn_entity(npc_components)
       # self.spawn_entity(npc_components)

                


if __name__ == "__main__":
    meow = generate_hollow_rectangle(2,2,(-1,-1,0))
    for x in meow:
        print(x)