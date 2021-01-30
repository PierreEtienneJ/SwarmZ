
from swarmz_simulator.collision import *
from swarmz_simulator.vector import Vector
from swarmz_simulator.object import Object
from swarmz_simulator.communication import Communication
from swarmz_simulator.radar import Radar, Lidar

import numpy as np
import math
import random


class Drone:
    """this class corespond to a drone, can simulate there deplacement"""
    def __init__(self, position:Vector, speed:Vector, radius:float, name="", color=(-1,-1,-1), **kwargs):
        ##robot state
        self.position=position
        self.speed=speed
        self.next_position=position.copy()
        self.next_speed=speed.copy()

        self.motorPower=Vector(0,0)
        self.acceleration=Vector(0,0)

        self.capCommande=self.speed.cap()
        self.PIDcap=[0,0,0] #P I D
        self.angularCommande=0 #angle of rubber or pumpjet
        self.commandePower=0
        
        ##before quaternion implementation :/ 
        self.angularAcceleration=0
        self.angularSpeed=0
        self.angular=kwargs.get('ini_cap',self.speed.cap())
        
        self.arrive=False
        self.Dt=0

        #environement 
        self.nearDrones=[]
        self.nearObjects=[]
        self.goal=None

        #caracteristics 
        self.radius=abs(radius)
        self.radar=Lidar(10,int(360/5))

        self.communication=Communication(size_bufferRX=128,size_bufferTX=128)

        self.maxAcceleration=kwargs.get("maxAcceleration",0.1)
        self.maxAngularAcceleration=kwargs.get("maxAngularAcceleration",0.1)
        self.maxSpeed=kwargs.get("maxSpeed",2)
        self.maxAngularSpeed=kwargs.get("maxAngularSpeed",1)
        self.maxOpeningAngle=kwargs.get("maxOpeningAngle",30*math.pi/180) #rudder or pump jet opening angle
        
        self.mass=kwargs.get("mass",10) #kg
        self.moment_inertia=kwargs.get("Moment_inertia",10) #kg.m^2
        
        self.projected_area_x=kwargs.get("projected_area_x",6*math.pi*self.radius) #area of a sphere
        self.projected_area_y=kwargs.get("projected_area_y",10*self.projected_area_x) #10 x
        

        self.pumpJet=kwargs.get("pumpJet",True)

        self.rudder_height=kwargs.get("rudder_height",0)
        self.rudder_width=kwargs.get("rudder_width",0)

        self.positionOfRudder=kwargs.get("positionOfRudder",-0.1)

        self.maxPowerMotor=kwargs.get("maxPowerMotor",10) #in N

        #afin de mesurer le score
        self.nb_collisions=0
        self.T=0 #temps de trajet 
        self.__initPosition=self.position.copy()
        self.mean_speed=0
        self.__nb_actualization=0
        self.time=0
        #autre
        if name=="":
            self.name="drone_"+str(random.randint(0,10))
        else:
            self.name=name
        
        if color==(-1,-1,-1):
            self.color=(255,random.randint(20,80), random.randint(0,50))
        else:
            self.color=color

        ####history 
        self.history={"speed" : [], "cap": [], "position" : [], "time": [], "fitness":[]}
        self.dt=0
        
    def set_next(self):
        """if this drone was not colisioned, they can move at the next position
        """
        self.position=self.next_position.copy()
        self.speed=self.next_speed.copy()
        
        self.mean_speed=(self.mean_speed*self.__nb_actualization+self.speed.norm_2())/(self.__nb_actualization+1)
        
        self.__nb_actualization+=1

    def update(self, dt, coefTime)->None:
        """calcul the next position with they speed and time

        Args:
            dt (float): step time to set next position
        """
        while(self.angularCommande>=math.pi):
            self.angularCommande-=2*math.pi
        while(self.angularCommande<=-math.pi):
            self.angularCommande+=2*math.pi

        if(self.commandePower<self.maxPowerMotor):
            self.motorPower=Vector(self.commandePower,0)
        else:
            self.motorPower=Vector(self.maxPowerMotor,0)

        self.IA(dt=dt, coefTime=coefTime)
        
        if(not self.arrive):
            self.T+=dt*coefTime
        self.dt+=dt*coefTime
        self.time+=dt*coefTime
        
        if(self.dt>1):
            self.dt=0
            self.history["speed"].append(self.speed.norm_2())
            self.history["cap"].append(self.getCap())
            self.history["position"].append(self.position.copy())
            self.history["time"].append(self.time)
            self.history["fitness"].append(self.fitness())
            
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

        self.mean_speed=(self.mean_speed*self.__nb_actualization)/(self.__nb_actualization+1)
        self.__nb_actualization+=1


        delta=(2*random.random()-1)*math.pi/12
        
        #self.speed.setCap(self.speed.cap()+delta-math.pi)

        self.next_position=self.position.copy()
        self.speed.setNorm(self.speed.norm_2()/2)
        self.next_speed=self.speed.copy()
        
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
            pos.setCap(pos.cap()-self.getCap())
            list_drones.append(Drone(pos, Vector(0,0),drone.radius))

        list_objects=[]
        for obj in self.nearObjects:
            P=[]
            for point in obj.list_Points:
                pos=point.add(self.position.x_scal(-1))
                pos.setCap(pos.cap()-self.getCap())
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
        distanceParcouru=self.mean_speed*self.T
        if(self.goal!=None): 
            #la fct est décroissante de la distance de parcouru
            A=-1
            B=3
            #note+=A*distanceParcouru/self.__initPosition.distance(self.goal)+B
            if(self.position.distance(self.__initPosition)!=0):
                note+=A*distanceParcouru/self.position.distance(self.__initPosition)+B
            #la fct est décroissante de la distance restante
            if(not self.arrive):
                C=-1
                D=3
                note+=C*self.position.distance(self.goal)/self.__initPosition.distance(self.goal)+D
            else:
                E=-0.5
                F=60*4
                note+=(E*self.T+F)
        else: #la fct est croissante de la distance effectué
            A=0.2
            B=0
            note+=A*distanceParcouru+B
            
        note-=self.nb_collisions
        
        return note

    def IA(self,**kwargs):
        dt=kwargs.get('dt', 1e-50)
        coefTime=kwargs.get('coefTime', 1)
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


    def getCap(self):
        return self.angular