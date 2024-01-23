from typing import Tuple
from components import *
import random


 
def character_components( ):
    
    return { 
              Renderable : Renderable( "@", (255, 255, 255),prior = 9),
             
             Is_Player : Is_Player(),
             Collideable : Collideable(),
             Planned_Actions : Planned_Actions([]),
             Health : Health(87,100),
             Gravitational : Gravitational(),
             In_Overworld : In_Overworld()
    }

def npc_components( ):

    return {  
              Renderable : Renderable( "𔒒", (100, 50, 255),prior = 9),
              
              Collideable : Collideable(),
              Planned_Actions : Planned_Actions([]),
              Health : Health(100,100),
              Gravitational : Gravitational(),
              In_Overworld : In_Overworld()  
    }

def sandstone_wall( ):

    return {  
              Renderable : Renderable( "█", (50, 20, 30), (50, 20, 30),prior = 2),
              
              Collideable : Collideable(),
              Terrain: Terrain(),
              BlocksSight : BlocksSight(),
              Wall : Wall()
    }




def dirt_block( ):

    return {  
              Renderable : Renderable( "█", (125, 87, 57), (125, 87, 57),prior = 1),
              Terrain: Terrain(),
              Floor: Floor()
              
          #    Collideable : Collideable()
    }

def water_block( ):

    return {  
              Renderable : Renderable( "▓", (65, 124, 242), (55, 104, 222)),
              
       #       Collideable : Collideable()
    }



def sandstone_passage( ):

    return {  
              Renderable : Renderable( "𓊀", (227, 55, 43),prior = 7),
              In_Overworld : In_Overworld()
    }

def door_sign( ):

    return {  
              Renderable : Renderable( "+", (227, 55, 43),prior = 7),
              In_Overworld : In_Overworld()
    }

def egyptian_chest( ):

    return {  
              Renderable : Renderable( "𓊬", (52, 155, 235),prior = 5),
              
              Collideable : Collideable(),
              In_Overworld : In_Overworld()
    }

def egyptian_stool( ):

    return {  
              Renderable : Renderable( "𓊪", (52, 155, 235),prior = 5),
              
              Collideable : Collideable(),
              In_Overworld : In_Overworld()
    }

def egyptian_brazier( ):

    return {  
              Renderable : Renderable( "𓊮", (52, 155, 235),prior = 5),
              
              Collideable : Collideable(),
              In_Overworld : In_Overworld()
    }

def egyptian_bowl_with_smoke( ):

    return {  
              Renderable : Renderable( "𓊸", (52, 155, 235),prior = 5),
              
              Collideable : Collideable(),
              In_Overworld : In_Overworld()
    }
def egyptian_low_table( ):

    return {  
              Renderable : Renderable( "𓊳", (52, 155, 235),prior = 5),
              
              Collideable : Collideable(),
              In_Overworld : In_Overworld()
    }

def egyptian_low_table_offerings( ):

    return {  
              Renderable : Renderable( "𓊴", (52, 155, 235),prior = 5),
              
              Collideable : Collideable(),
              In_Overworld : In_Overworld()
    }

def egyptian_loaf_on_mat( ):

    return {  
              Renderable : Renderable( "𓊵", (52, 155, 235),prior = 5),
              
              Collideable : Collideable(),
              In_Overworld : In_Overworld()
    }


####component groups

def egyptian_common_furniture():
    
    return {egyptian_loaf_on_mat,egyptian_low_table_offerings,egyptian_low_table,egyptian_bowl_with_smoke,egyptian_brazier,egyptian_stool,egyptian_chest}