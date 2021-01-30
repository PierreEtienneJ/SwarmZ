import pygame
import math
import time
import threading
import statistics
import random

from swarmz_simulator.vector import Vector
from swarmz_simulator.drone import Drone
from swarmz_simulator.simulator import PhysicalSimulator,RadarSimulator, CommunicationSimulator
from swarmz_simulator.display import Display, EventDisplay
from swarmz_simulator.object import Object
from swarmz_simulator.environment import Environment
from swarmz_simulator.radar import Radar, Lidar 

def setRad(rad:float)->float:
    """take a angle and return this angle between -pi and pi 

    Args:
        rad (float): [description]
    """
    while(rad>math.pi):
        rad-=2*math.pi
    while(rad<-math.pi):
        rad+=2*math.pi
    return rad

class MyDrone(Drone):
    """How create a specific drone
    """
    def __init__(self,position:Vector, **kwargs):
        super().__init__(position, Vector(0.5,0), 0.2,name="R2D2",color=(50,50,100), **kwargs) #initialize the drone 
        self.radar=Radar(10,[0,math.pi/2,math.pi, -math.pi/2, math.pi/6, -math.pi/6]) #create specific Radar
        self.PIDcap=[0,0,0]  #err PID 
        self.Dt=10
        self.commandePower=20
        
    def IA(self,**kwargs):
        """create one specific IA
        all 10s, if the shortest ray are less than 2m, the drone turn of 90deg as the angle of this ray else, 
        he take cap of the goal whith a random 
        """
        dt=kwargs.get('dt', 1e-50)
        coefTime=kwargs.get('coefTime', 1)
        
        if(dt==0):
            dt=1e-50
        if(self.arrive):
            self.next_speed.setNorm(1e-50)
            self.color=(0,0,0)
            
        else:
            if(self.Dt>10):
                self.Dt=0
                indice_ray_proche=sorted(range(len(self.radar.rays)), key=lambda k: self.radar.rays[k]) #sorted of ray indice by ray distance
                if(self.radar.rays[indice_ray_proche[0]]<2): 
                    #print("obstacle: ", self.radar.angles_[indice_ray_proche[0]]*180/math.pi, 
                    #(self.radar.angles_[indice_ray_proche[0]]+self.getCap())*180/math.pi, self.radar.rays[indice_ray_proche[0]])
                    self.setCap(self.radar.angles_[indice_ray_proche[0]]+self.getCap()+math.pi/2) #new cap
                elif(self.goal):
                    cap_goal=Vector(self.goal.x-self.next_position.x, self.goal.y-self.next_position.y).cap()
                    self.setCap(cap_goal+(2*random.random()-1)*math.pi/6)
                else:
                    self.setCap((2*random.random()-1)*math.pi/4 + self.getCap())
                self.commandePower=20

                L=[random.randint(0,1) for i in range(10)]
                #print("====================================")
                #print(self.name)
                for e in L:
                    self.communication.addTX(e)
                #print("send :", L, "buffer TX=", self.communication.bufferTX.tableau)
                T=[]
                #print("buffer RX=", self.communication.bufferRX.tableau)
                while self.communication.haveMsg():
                    T.append(self.communication.getMsg())
                #print("recive : ", T)

            self.Dt+=dt*coefTime
            self.T+=dt*coefTime
        
            ###### PID cap
            P=1
            I=0.1
            D=0
            self.capCommande=setRad(self.capCommande)
            self.angular=setRad(self.angular)
            err=self.angular-self.capCommande
            err=setRad(err)
            
            #commande of the ange of pumpjet 
            self.angularCommande=P*err+I*(self.PIDcap[1]+err*dt)+D*(err-self.PIDcap[2])/dt
            self.PIDcap[1]+=err*dt
            self.PIDcap[2]=err
            
            self.angularCommande=setRad(self.angularCommande)
            
           # print(self.speed.norm_2())
            
    def setCap(self, cap):
        cap=setRad(cap)
        self.capCommande=cap
        self.PIDcap=[0,0,0]

    def collision(self):
        self.speed=Vector(0,0)

def getInitialPosition(n, eps, center=Vector(0,0)):
    ###répartie en carré de n drones éloigner de eps
    positions=[]
    a=n%2
    b=n%4
    for i in range(n//4+b):
        positions.append(Vector(n/8-i, -n/4).x_scal(eps).add(center))
    for i in range(n//4):
        positions.append(Vector(n/8-i, n/4).x_scal(eps).add(center))
    for j in range(n//4+a):
        positions.append(Vector(-n/8, -n/8+j).x_scal(eps).add(center))
    for j in range(n//4):
        positions.append(Vector(n/8, -n/8+j).x_scal(eps).add(center))
    
    while len(positions)>n:
        positions.pop()
    return positions
 
 
if __name__ == '__main__':
    if(True):
        obj=Object([Vector(5,5), Vector(3,5), Vector(3,3), Vector(5,3), Vector(7,5)])
        obj1=Object([Vector(-10,5), Vector(-13,5), Vector(-5,3)])
        obj2=Object([Vector(-5,-5), Vector(-3,-5), Vector(-3,-3), Vector(-5,-3), Vector(-7,-5)])

        goal=Object([Vector(10,10), Vector(8,10), Vector(8,8), Vector(10,8)])

        #creation du sim
        env=Environment([], [obj, obj1, obj2], goal)
        
        positions=getInitialPosition(20, 1)
        
        for i in range(2):
            env.add(MyDrone(positions[i], pumpJet=True, maxPowerMotor=1,positionOfRudder=-0.2,
                              moment_inertia=0.1,maxOpeningAngle=30*math.pi/180))
            
        
    else:
        env=Environment()
        env.load("env_1", class_drone=MyDrone)
        
    
        
    eventFenetre=EventDisplay()

    physicalSimu=PhysicalSimulator(env, eventFenetre)
    radarSim=RadarSimulator(env, eventFenetre)
    comSim=CommunicationSimulator(env, eventFenetre)
    fenetre = Display(env, eventFenetre)
    
    physicalSimu.start()
    radarSim.start()
    comSim.start()

    fenetre.run()
    
    physicalSimu.join()
    radarSim.join()
    comSim.join()
    pygame.quit()
    

