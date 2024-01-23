import time
import numpy as np


def get_orthonormal_pair(vector):
    dir_vec = np.array(vector)
    first_ortho = np.random.randn(3) 
    first_ortho -= first_ortho.dot(dir_vec) * dir_vec  / np.linalg.norm(dir_vec)**2     # make it orthogonal to k
    first_ortho /= np.linalg.norm(first_ortho) 
    second_ortho = np.cross(dir_vec, first_ortho)
    second_ortho /= np.linalg.norm(second_ortho) 

    return (first_ortho,second_ortho)




def algoslol():
    start_time = time.time()
    (x1, y1, z1) = (0, 0, 0)
    (x2, y2, z2) = (20, 50, 10)
    ListOfPoints = Bresenham3D(x1, y1, z1, x2, y2, z2)
    end_time = time.time()
    elapsed_time = end_time-start_time



   # (x1, y1, z1) = (-7, 0, -3)
    #(x2, y2, z2) = (200000, -500000, -100000)
    #ListOfPoints = Bresenham3D(x1, y1, z1, x2, y2, z2)
    #end_time = time.time()
    #elapsed_time = end_time-start_time

    print(ListOfPoints)

    print("ELAPSED TIME IS")
    print(elapsed_time)
    print(len(ListOfPoints))

    desu = (20, 50, 10)
    lol = get_orthonormal_pair(desu)
   # print(np.dot(desu,lol[0]))
   # print(np.dot(desu,lol[1]))
   # print(np.dot(lol[1],lol[0]))
   # print(lol[0])
   # print(lol[1])



if __name__ == "__main__":
    algoslol()