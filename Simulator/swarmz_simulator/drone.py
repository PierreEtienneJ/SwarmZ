
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
    def __init__(self, position:Vector, speed:Vector, radius:float, name="", color=(-1,-1,-1), **kwargs):
        ##robot state
        self.position=position
        self.speed=speed
        self.next_position=position
        self.next_speed=speed

        self.motorPower=Vector(0,0)
        self.acceleration=Vector(0,0)

        self.capCommande=self.speed.cap()
        self.PIDcap=[0,0,0] #P I D
        self.angularCommande=0 #angle of rubber or pumpjet
        self.commandePower=0
        
        ##before quaternion implementation :/ 
        self.angularAcceleration=0
        self.angularSpeed=0
        self.angular=self.speed.cap()
        
        self.arrive=False
        self.Dt=0

        #environement 
        self.nearDrones=[]
        self.nearObjects=[]
        self.goal=None

        #caracteristics 
        self.radius=abs(radius)
        self.radar=Lidar(10,int(360/5))

        self.maxAcceleration=kwargs.get("maxAcceleration",0.1)
        self.maxAngularAcceleration=kwargs.get("maxAngularAcceleration",0.1)
        self.maxSpeed=kwargs.get("maxSpeed",1)
        self.maxAngularSpeed=kwargs.get("maxAngularSpeed",1)
        self.maxOpeningAngle=kwargs.get("maxOpeningAngle",30*math.pi/180) #rudder or pump jet opening angle
        
        self.mass=kwargs.get("mass",10) #kg
        self.moment_inertia=kwargs.get("Moment_inertia",10) #kg.m^2
        
        self.dynamic_viscosity=kwargs.get("dynamic_viscosity",1e-3) #dynamic viscosity of water

        self.projected_area=kwargs.get("projected_area",6*math.pi*self.radius) #area of a sphere

        self.gravity=9.80665 #constant if gravity in earth

        self.pumpJet=kwargs.get("pumpJet",True)

        self.rudder_height=kwargs.get("rudder_height",0)
        self.rudder_width=kwargs.get("rudder_width",0)

        self.positionOfRudder=kwargs.get("positionOfRudder",-0.1)

        self.maxPowerMotor=kwargs.get("maxPowerMotor",10) #in N

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
        self.position=self.next_position.copy()
        self.speed=self.next_speed.copy()
        
        self.__mean_speed=(self.__mean_speed*self.__nb_actualization+self.speed.norm_2())/(self.__nb_actualization+1)
        
        self.__nb_actualization+=1

    def update(self, dt)->None:
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
        
        K=0
        if(self.pumpJet):
            if(-self.maxOpeningAngle<self.angularCommande<self.maxOpeningAngle):
                self.motorPower.setCap(self.angularCommande)
            elif(self.angularCommande<0):
                self.motorPower.setCap(-self.maxOpeningAngle)
            else:
                self.motorPower.setCap(self.maxOpeningAngle)

        else:
            if(-self.maxOpeningAngle<self.angularCommande<self.maxOpeningAngle):
                K=self.rudder_height*self.rudder_width*math.sin(self.angularCommande)

            elif(self.angularCommande<0):
                K=self.rudder_height*self.rudder_width*math.sin(-self.maxOpeningAngle)
            else:
                K=self.rudder_height*self.rudder_width*math.sin(self.maxOpeningAngle)
            K=K*1e7
            

        ####________________________
        ###             PFD 
        ####________________________
        if(self.speed.norm_2()<1):
            alpha=1
        elif(self.speed.norm_2()<2):
            alpha=1.4 #wikipedia
        else:
            alpha=2

        ##we set new referential : xb, yb referential of boat  

        ##frottement fluid = -S mu * V**alpha
        local_speed=self.speed.copy()
        local_speed.setCap(self.speed.cap()-self.angular)
        local_speed_n=local_speed.copy()
        local_speed_n.setNorm(1)

        fluidFriction_x=-self.projected_area*self.dynamic_viscosity*abs(local_speed.x)**alpha
        fluidFriction_y=-1e4*self.projected_area*self.dynamic_viscosity*abs(local_speed.y)**(alpha)

        if(local_speed.x<0):
            fluidFriction_x=-fluidFriction_x
        if(local_speed.y<0):
            fluidFriction_y=-fluidFriction_y

        self.acceleration=Vector(fluidFriction_x,fluidFriction_y).add(self.motorPower).x_scal(1/self.mass)
        
        #self.angularAcceleration=(self.motorPower.y*self.positionOfRudder+K*self.positionOfRudder*self.dynamic_viscosity*self.speed.norm_2()**1)/self.moment_inertia
        moment_motor=self.motorPower.y*self.positionOfRudder
        moment_derive=-self.positionOfRudder*fluidFriction_y
        self.angularAcceleration=(moment_motor+moment_derive)/self.moment_inertia

        #print("speed :", self.speed.x,self.speed.y,self.speed.cap()*180/math.pi)
        #print("local speed :", local_speed.x,local_speed.y, local_speed.cap()*180/math.pi)
        #print("motor : ", self.motorPower.x,self.motorPower.y)
        #print("friction: ",fluidFriction_x,fluidFriction_y)
        
        #print("acc local: ", self.acceleration.x,self.acceleration.y)
        
        a=self.angular
        #print("K:", K)
        """
        if(self.acceleration.norm_2()>self.maxAcceleration):
            self.acceleration.setNorm(self.maxAcceleration)
        if(self.angularAcceleration>self.maxAngularAcceleration):
            self."""
        
        self.acceleration.setCap(self.acceleration.cap()+self.angular)

        self.next_speed=self.speed.add(self.acceleration.x_scal(dt))
        
        if(self.next_speed.norm_2()>self.maxSpeed):
            self.next_speed.setNorm(self.maxSpeed)

        self.angularSpeed=self.angularAcceleration*dt
        self.angular+=1/2*self.angularAcceleration*dt
        

        #print("agular, angular acc",self.angular*180/math.pi,self.angularAcceleration)
        #print("dalpha: ,", a-self.angular)
        #print("agular speed", self.angularSpeed)

        self.next_position.x=self.position.x+self.acceleration.x_scal(dt**2/2).x #+self.speed.x_scal(dt).x
        self.next_position.y=self.position.y+self.acceleration.x_scal(dt**2/2).y

        self.IA(dt=dt)

        
        #print("New")
        #print("vitesse",self.speed.x,self.speed.y, "new", self.next_speed.x,self.next_speed.y)
        #print("acceleration", self.acceleration.x, self.acceleration.y)

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

    def getCap(self):
        return self.angular