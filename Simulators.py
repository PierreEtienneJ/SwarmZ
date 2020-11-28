
# %%
import math
import threading
import time

from Drones import Drone
from Objects import Object
from Vectors import Vector
from Environements import Environment
from Fenetres import EventFenetre

class Simulator(threading.Thread):
    def __init__(self, environement, eventFenetre):
        """Simulator need one environment, he check colision between drone and drone and drones
        between drone and object"""
        threading.Thread.__init__(self)
        
        self.environement=environement
        self.eventFenetre=eventFenetre

    def update(self, dt)->list:
        """Here, we update next position for all drones with dt and check all collisions 
        dt was time betwenn now and previous position"""
        for i in range(self.environement.nb_drones):
            self.environement.drones[i].update(dt)
        
        collision_D_D=[]
        collision_D_Obj=[]
        for i in range(self.environement.nb_drones-1):
            for j in range(i+1,self.environement.nb_drones):
                if(self.collision_Drone_Drone(i,j)):
                    collision_D_D.append(i)
                    collision_D_D.append(j)

            for j in range(self.environement.nb_objects):
                if(self.collision_Drone_Objects(i,j)):
                    collision_D_Obj.append(i)

        for i in range(self.environement.nb_drones):
            if(i in collision_D_D or i in collision_D_Obj):
                self.environement.drones[i].collision()
            else:
                self.environement.drones[i].set_next()

        return (collision_D_D, collision_D_Obj)

    def collision_Drone_Drone(self, i:int,j:int):
        """Here we check colision between two drones : drone i and drone j in the list of drones"""
        next_distance=self.environement.drones[i].next_position.distance(self.environement.drones[j].next_position)

        if(next_distance<self.environement.drones[i].get_rayon()+self.environement.drones[j].get_rayon()):
            return True
        else:
            return False

    def collision_Drone_Objects(self,i:int, j:int):
        """Here we check collision betwen drone i in the list of drone and the object j in the list of objects
        2 step :- we check collision between drone and object considered as a circle 
                - they are collision, we check more precisely if they are a collision. 
                """
        distance=self.environement.drones[i].next_position.distance(self.environement.objects[j].center)

        if(distance<self.environement.drones[i].get_rayon()+self.environement.objects[j].rayon):
            return True
        else:
            return False

    def run(self):
        t1=t0=time.time() #save time

        while(not self.eventFenetre.stop):
            if(not self.eventFenetre.pause):
                self.update(self.eventFenetre.dt*self.eventFenetre.coefTime)
            t1=time.time()
        
        self.stop()

    def stop(self):
        self.eventFenetre.stop=True
      #  self.join()  

