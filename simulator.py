
# %%
import math
import threading
import time
import random
import statistics

from drone import Drone
from object import Object
from vector import Vector
from environment import Environment
from display import EventDisplay
from collision import *

class Simulator(threading.Thread):
    def __init__(self, environment:"Environment", eventDisplay:"display.EventDisplay"):
        """Simulator need one environment, he check colision between drone and drone and drones
        between drone and object"""
        threading.Thread.__init__(self)
        
        self.environment=environment
        self.eventDisplay=eventDisplay

        self.T=[]
    def update(self, dt)->list:
        """Here, we update next position for all drones with dt and check all collisions 
        dt was time betwenn now and previous position"""
        for i in range(self.environment.nb_drones):
            self.environment.drones[i].update(dt)
        
        collision_D_D=[]
        collision_D_Obj=[]
        
        for i in range(self.environment.nb_drones):
            if(i!=self.environment.nb_drones-1): #si ce n'est pas le dernier drone
                for j in range(i+1,self.environment.nb_drones):
                    if(self.collision_Drone_Drone(i,j)):
                        collision_D_D.append(i)
                        collision_D_D.append(j)

            for j in range(self.environment.nb_objects):
                if(self.collision_Drone_Objects(i,j)):
                    collision_D_Obj.append(i)

            if(self.environment.goal_has_def()):
                if self.droneGoal(i):
                    self.environment.drones[i].setGoal()

      #  lead=random.randint(0,self.environment.nb_drones-1)
        for i in range(self.environment.nb_drones):
            if(i in collision_D_D or i in collision_D_Obj):
                self.environment.drones[i].collision()
            else:
             #   if(i!=lead):
             #       self.environment.drones[i].next_vitesse.setCap(self.environment.drones[lead].vitesse.cap())
                self.environment.drones[i].set_next()
                
            self.environment.drones[i].setEnvironment(self.environment.nearEnv(self.environment.drones[i].position, self.environment.drones[i].radar.range_))
                

        

        return (collision_D_D, collision_D_Obj)

    def collision_Drone_Drone(self, i:int,j:int):
        """Here we check colision between two drones : drone i and drone j in the list of drones"""
        next_distance=self.environment.drones[i].next_position.distance(self.environment.drones[j].next_position)
    
        if(next_distance<=(self.environment.drones[i].get_radius()+self.environment.drones[j].get_radius())):
            x=self.environment.drones[i].next_speed.x*self.environment.drones[j].next_speed.x
            y=self.environment.drones[i].next_speed.y*self.environment.drones[j].next_speed.y

            if(x<0 or y<0):
                        ##si les vitesses ne convergent pas ni quelles sont dans le meme sens
                return False
            else:
                return True
        else:
            return False

    def __collisionDroiteCercle(self,A:"vector.Vector",B:"vector.Vector",P:"vector.Vector", r:float)->bool:
        """We look to see if there is a collision between the circle of radius r and center P with the segment A,B"""
        n=abs((B.x-A.x)*(P.y-A.y)-(B.y-A.y)*(P.x-A.x))
        d=math.sqrt((B.x-A.x)**2+(B.y-A.y)**2) #norme de AB
        if(n/d>r):
            return False

        p1=(B.x-A.x)*(P.x-A.x)+(P.y-A.y)*(B.y-A.y)
        p2=-(B.x-A.x)*(P.x-B.x)-(P.y-B.y)*(B.y-A.y)
        if p1>=0 and p2>=0:
            return True
        
        if((A.x-P.x)**2+(A.y-P.y)**2<r**2):
            return True
        if((B.x-P.x)**2+(B.y-P.y)**2<r**2):
            return True

        return False 
    
    def collision_Drone_Objects(self,i:int, j:int):
        """Here we check collision betwen drone i in the list of drone and the object j in the list of objects
        2 step :- we check collision between drone and object considered as a circle 
                - they are collision, we check more precisely if they are a collision. 
                """
        distance=self.environment.drones[i].next_position.distance(self.environment.objects[j].center)

        if(distance<self.environment.drones[i].get_radius()+self.environment.objects[j].radius):
            """si il y a collision entre les cercles du drone et de l'objet, on regarde si il y a une vrai collision"""
            #//https://openclassrooms.com/fr/courses/1374826-theorie-des-collisions/1375352-formes-plus-complexes page fermé :/

            A=self.environment.objects[j].list_Points[0]
            for l in range(1,len(self.environment.objects[j].list_Points)):
                B=self.environment.objects[j].list_Points[l]
                if(self.__collisionDroiteCercle(A,B,self.environment.drones[i].next_position, self.environment.drones[i].radius)): #si le robot colisionne avec la ligne
                    ##on verifie si le drone ne s'éloigne pas de la ligne
                    return True
                    #on calcul le point d'intersection entre V et (AB)
                    P=intersection(A,Vector(A.x-B.x, A.y-B.y), self.environment.drones[i].next_position, self.environment.drones[i].next_speed)
                    if(P==None):
                        return False
                    else:
                        x=self.environment.drones[i].next_position.x
                        y=self.environment.drones[i].next_position.y
                        vx=self.environment.drones[i].next_speed.x
                        vy=self.environment.drones[i].next_speed.y
                        (a,b,c)=droite(A,Vector(A.x-B.x, A.y-B.y))
                        

                        if(x<P.x):
                            if(b==0):
                                return vx>0
                            a,c=-a/b,-c/b
                            if(y<a*x+c): #si le point est sous la droite
                                return vx>0 #si il se dirige vers la droite
                            else:
                                return vx<0

                        else:
                            if(b==0):
                                return vx<0
                            a,c=-a/b,-c/b
                            if(y<a*x+c): #si le point est sous la droite
                                return vx<0 #si il se dirige vers la droite
                            else:
                                return vx>0
                    
                A=B
            return self.__collisionDroiteCercle(A,self.environment.objects[j].list_Points[0],self.environment.drones[i].next_position, self.environment.drones[i].radius)
                
        else:

            return False

    def droneGoal(self, i:int):
        """check if the drone i achieve the goal"""
        distance=self.environment.drones[i].next_position.distance(self.environment.goal.center)

        if(distance<self.environment.drones[i].get_radius()+self.environment.goal.radius):
            """si il y a collision entre les cercles du drone et de l'objet, on regarde si il y a une vrai collision"""
            #//https://openclassrooms.com/fr/courses/1374826-theorie-des-collisions/1375352-formes-plus-complexes page fermé :/

            A=self.environment.goal.list_Points[0]
            for l in range(1,len(self.environment.goal.list_Points)):
                B=self.environment.goal.list_Points[l]
                if(self.__collisionDroiteCercle(A,B,self.environment.drones[i].next_position, self.environment.drones[i].radius)): #si le robot colisionne avec la ligne
                    ##on verifie si le drone ne s'éloigne pas de la ligne
                    return True
                    #on calcul le point d'intersection entre V et (AB)
                    P=intersection(A,Vector(A.x-B.x, A.y-B.y), self.environment.drones[i].next_position, self.environment.drones[i].next_speed)
                    if(P==None):
                        return False
                    else:
                        x=self.environment.drones[i].next_position.x
                        y=self.environment.drones[i].next_position.y
                        vx=self.environment.drones[i].next_speed.x
                        vy=self.environment.drones[i].next_speed.y
                        (a,b,c)=droite(A,Vector(A.x-B.x, A.y-B.y))
                        

                        if(x<P.x):
                            if(b==0):
                                return vx>0
                            a,c=-a/b,-c/b
                            if(y<a*x+c): #si le point est sous la droite
                                return vx>0 #si il se dirige vers la droite
                            else:
                                return vx<0

                        else:
                            if(b==0):
                                return vx<0
                            a,c=-a/b,-c/b
                            if(y<a*x+c): #si le point est sous la droite
                                return vx<0 #si il se dirige vers la droite
                            else:
                                return vx>0
                    
                A=B
            return self.__collisionDroiteCercle(A,self.environment.goal.list_Points[0],self.environment.drones[i].next_position, self.environment.drones[i].radius)
                
        else:

            return False


    def run(self):
        t1=t0=time.time() #save time

        while(not self.eventDisplay.stop):
            if(not self.eventDisplay.pause):
                self.update(self.eventDisplay.dt*self.eventDisplay.coefTime)

                self.T.append(time.time()-t1)
            t1=time.time()
            if(len(self.T)>1000):
               # print("mean time update simu : ", 1/statistics.mean(self.T))
                self.T=[]
        self.stop()

    def stop(self):
        self.eventDisplay.stop=True

