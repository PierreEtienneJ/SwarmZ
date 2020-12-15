import pygame
import math
import time
import threading
import statistics
import random

from swarmz_simulator.vector import Vector
from swarmz_simulator.drone import Drone
from swarmz_simulator.simulator import Simulator
from swarmz_simulator.display import Display, EventDisplay
from swarmz_simulator.object import Object
from swarmz_simulator.environment import Environment
from swarmz_simulator.radar import Radar, Lidar 

def setRad(rad:float)->float:
    """take a angle and return this angle between -pi and pi 

    Args:
        rad (float): [description]
    """
    while(rad>=math.pi):
        rad-=2*math.pi
    while(rad<=-math.pi):
        rad+=2*math.pi
    return rad

class MyDrone(Drone):
    """How create a specific drone
    """
    def __init__(self,position:Vector, **kwargs):
        super().__init__(position, Vector(0.5,0), 0.2,name="R2D2",color=(50,50,100), **kwargs)
        self.radar=Radar(10,[0,math.pi/2,math.pi, -math.pi/2, math.pi/6, -math.pi/6])
        self.PIDcap=[0,0,0]
        self.Dt=50
        self.commandePower=20

    def IA(self,**kwargs):
        """create one specific IA
        """
        dt=kwargs.get('dt', 0)
        if(dt==0):
            dt=1e-50
        if(self.arrive):
            self.next_speed.setNorm(0)
            self.color=(0,0,0)
        else:
            if(self.Dt>50):
                self.Dt=0
                indice_ray_proche=sorted(range(len(self.radar.rays)), key=lambda k: self.radar.rays[k])
                if(self.radar.rays[indice_ray_proche[0]]<2):
                    print("obstacle: ", self.radar.angles_[indice_ray_proche[0]]*180/math.pi, 
                    (self.radar.angles_[indice_ray_proche[0]]+self.getCap())*180/math.pi, self.radar.rays[indice_ray_proche[0]])
                    self.setCap(self.radar.angles_[indice_ray_proche[0]]+self.getCap()+math.pi/2)
                elif(self.goal):
                    cap_goal=Vector(self.goal.x-self.next_position.x, self.goal.y-self.next_position.y).cap()
                    self.setCap(cap_goal+(2*random.random()-1)*math.pi/6)
                else:
                    self.setCap((2*random.random()-1)*math.pi/4)
                self.commandePower=20
            
            if(self.T>50000):
                self.angularCommande=0
                self.commandePower=0
            self.Dt+=dt
            self.T+=dt
        
            ###### PID cap
            P=1
            I=0.1
            D=0
            err=self.angular-self.capCommande
            err=setRad(err)
            self.angularCommande=P*err+I*(self.PIDcap[1]+err*dt)+D*(err-self.PIDcap[2])/dt
            self.PIDcap[1]+=err*dt
            self.PIDcap[2]=err

    def setCap(self, cap):
        cap=setRad(cap)

        self.capCommande=cap
        self.PIDcap=[0,0,0]

    def collision(self):
        self.speed=Vector(0,0)
 
if __name__ == '__main__':
   
    if(True):
        drone1=MyDrone(Vector(1,0), pumpJet=True, rudder_height=1, rudder_width=0.05,
        maxPowerMotor=1,positionOfRudder=-0.2,moment_inertia=0.5,maxOpeningAngle=30*math.pi/180)

        drone2=MyDrone(Vector(-1,0), pumpJet=True, rudder_height=1, rudder_width=0.05,
        maxPowerMotor=1,positionOfRudder=-0.2,moment_inertia=0.5,maxOpeningAngle=30*math.pi/180)

        drone3=MyDrone(Vector(0,1), pumpJet=True, rudder_height=1, rudder_width=0.05,
        maxPowerMotor=1,positionOfRudder=-0.2,moment_inertia=0.5,maxOpeningAngle=30*math.pi/180)

        drone4=MyDrone(Vector(0,-1), pumpJet=True, rudder_height=1, rudder_width=0.05,
        maxPowerMotor=1,positionOfRudder=-0.2,moment_inertia=0.5,maxOpeningAngle=30*math.pi/180)
        drone4.radar=Lidar(20,36)
        
        #creation des obstacles, liste des coins
        obj=Object([Vector(5,5), Vector(3,5), Vector(3,3), Vector(5,3), Vector(7,5)])
        obj1=Object([Vector(-10,5), Vector(-13,5), Vector(-5,3)])
        obj2=Object([Vector(-5,-5), Vector(-3,-5), Vector(-3,-3), Vector(-5,-3), Vector(-7,-5)])

        goal=Object([Vector(10,10), Vector(8,10), Vector(8,8), Vector(10,8)])

        #creation du sim
        env=Environment([drone2,drone3], [obj, obj1], goal) 

        env.add(drone1)
        env.add(obj2)
        env.add(drone4)
        
    else:
        env=Environment()
        env.load("env_1", class_drone=MyDrone)
        
    eventFenetre=EventDisplay()

    simu=Simulator(env, eventFenetre)

    fenetre = Display(env, eventFenetre)
    
    simu.start()
    fenetre.run()
    simu.join()
    pygame.quit()
    

