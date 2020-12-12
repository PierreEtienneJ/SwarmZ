
from swarmz_simulator.collision import *
from swarmz_simulator.vector import Vector
from swarmz_simulator.object import Object
from swarmz_simulator.radar import Radar, Lidar

import numpy as np
import math
import random
import math

import matplotlib.pyplot as plt

class Drone:
    """this class corespond to a drone, can simulate there deplacement"""
    def __init__(self, position:Vector, speed:Vector, radius:float, name="", color=(-1,-1,-1)):
        self.position=position
        self.speed=speed
        self.radius=abs(radius)
        self.next_position=position
        self.next_speed=speed

        self.arrive=False
        
        self.nearDrones=[]
        self.nearObjects=[]
        self.goal=None

        self.radar=Lidar(10,int(360/5))

        self.Dt=0

        #afin de mesurer le score
        self.nb_collisions=0
        self.T=0 #temps de trajet 
        self.__initPosition=self.position
        self.__mean_speed=0
        self.__nb_actualization=0

        #autre
        if name=="":
            self.name="drone_"+str(random.randint(0,10))
        else:
            self.name=name
        
        if color==(-1,-1,-1):
            self.color=(255,random.randint(20,80), random.randint(0,50))
        else:
            self.color=color

    def set_next(self):
        """if this drone was not colisioned, they can move at the next position
        """
        
        self.position=self.next_position
        self.speed=self.next_speed
        
        self.__mean_speed=(self.__mean_speed*self.__nb_actualization+self.speed.norm_2())/(self.__nb_actualization+1)
        
        self.__nb_actualization+=1

    def update(self, dt)->None:
        """calcul the next position with they speed and time

        Args:
            dt (float): step time to set next position
        """
        
        self.next_position.x=self.position.x+self.speed.x_scal(dt).x
        self.next_position.y=self.position.y+self.speed.x_scal(dt).y

        self.IA(dt=dt)
        
    def setNextSpeed(self, new_speed:Vector)->None:
        """Set new_speed to the Drone

        Args:
            new_speed (Vector): new speed
        """
        self.next_speed=new_speed
    
    def getPosition(self)->Vector:
        """return the position"""
        return self.position
    
    def get_radius(self)->float:
        """return the radius"""
        return self.radius

    def setGoal(self):
         ##T temps de parcours
        self.arrive=True

    def collision(self)->None:
        """the drone collided with an obstacle. 
        """
        self.nb_collisions+=1

        self.__mean_speed=(self.__mean_speed*self.__nb_actualization)/(self.__nb_actualization+1)
        self.__nb_actualization+=1


        delta=(2*random.random()-1)*math.pi/12
        
        self.speed.setCap(self.speed.cap()+delta-math.pi)
        self.next_position=self.position
        self.next_speed=self.speed

    def setEnvironment(self, env:tuple)->None:
        """Set the nearby environment :
        Args:
            env (tuple (list(Drone), list(Object), Vector)): [description]
        """
        (self.nearDrones, self.nearObjects, self.goal)=env
        self.__updateRadar()
    
    def __updateRadar(self):
        list_drones=[]
        for drone in self.nearDrones:
            pos=drone.position.add(self.position.x_scal(-1))
            pos.setCap(pos.cap()-self.speed.cap())
            list_drones.append(Drone(pos, Vector(0,0),drone.radius))

        list_objects=[]
        for obj in self.nearObjects:
            P=[]
            for point in obj.list_Points:
                pos=point.add(self.position.x_scal(-1))
                pos.setCap(pos.cap()-self.speed.cap())
                P.append(pos)
            list_objects.append(Object(P))
        
        self.radar.update(list_Objects=list_objects, list_Drones=list_drones)

    def fitness(self):
        """notes the actions of the drone
        Returns:
            float: note
        """
        note=0
        #######################################
        ##paramètres :
        #######################################
        ###importance de la distance du parcours: 
        #si un goal à été défini 
        if(self.goal!=None): #la fct est décroissante de la distance de parcours
            A=-0.5
            B=+self.__initPosition.distance(self.goal)
        else: #la fct est croissante de la distance effectué
            A=0.2
            B=0

        #importance de l'essaim 
        C=-0.05

        if(not self.arrive):
            note-=1000 #le drone est jamais arrivé
        else:
            note+=A*self.__mean_speed*self.T+B

        return note

    def IA(self,**kwargs):
        dt=kwargs.get('dt', None)
        
        if(self.arrive):
            self.next_speed.setCap(self.speed.cap()+math.pi/12*dt)
            self.color=(255,random.randint(0,255), random.randint(0,255))

        else:
            if(self.Dt>5):
                self.Dt=0
                if(self.goal!=None):
                    self.next_speed.setCap(Vector(self.goal.x-self.next_position.x, self.goal.y-self.next_position.y).cap()+(2*random.random()-1)*math.pi/6)
            else:
                self.next_speed=self.speed

            self.Dt+=dt

        if(not self.arrive):
            self.T+=dt



        