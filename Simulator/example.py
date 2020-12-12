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
from swarmz_simulator.radar import Radar 

class MyDrone(Drone):
    """How create a specific drone
    """
    def __init__(self,position:Vector):
        super().__init__(position, Vector(0.5,0), 0.2,name="R2D2",color=(50,50,100))
        self.radar=Radar(10,[0,math.pi/2,math.pi, -math.pi/2, math.pi/6, -math.pi/6])
    
    def IA(self,**kwargs):
        """create one specific IA
        """
        dt=kwargs.get('dt', None)
        
        if(self.arrive):
            self.next_speed.setNorm(0)
            self.color=(0,0,0)
        else:
            if(self.Dt>5):
                self.Dt=0
                if(self.goal!=None):
                    self.next_speed.setCap(Vector(self.goal.x-self.next_position.x, self.goal.y-self.next_position.y).cap()+(2*random.random()-1)*math.pi/4)
            else:
                self.next_speed=self.speed
                if(min(self.radar.rays)<2):
                    if(self.speed.norm_2()<0.1):
                        self.next_speed.setNorm(0.1)
                    else:
                        self.next_speed.setNorm(self.speed.norm_2()*0.9)

                else:
                    if(self.speed.norm_2()<1):
                        self.next_speed.setNorm(self.speed.norm_2()*1.1)
                    else:
                        self.next_speed.setNorm(1)

            self.Dt+=dt

        if(not self.arrive):
            self.T+=dt




if __name__ == '__main__':
   
    if(True):
        drone1=MyDrone(Vector(0,0))
        drone2=Drone(Vector(1,1),Vector(0.5,0.5),0.2)
        drone3=Drone(Vector(0,1),Vector(0,-0.5),0.2)
        drone4=Drone(Vector(4,1),Vector(0,0.5),0.2)
        drone5=Drone(Vector(4,0),Vector(0.5,0),0.2)
        drone6=Drone(Vector(2,1),Vector(0.5,0),0.2)


        #creation des obstacles, liste des coins
        obj=Object([Vector(5,5), Vector(3,5), Vector(3,3), Vector(5,3), Vector(7,5)])
        obj1=Object([Vector(-10,5), Vector(-13,5), Vector(-5,3)])
        obj2=Object([Vector(-5,-5), Vector(-3,-5), Vector(-3,-3), Vector(-5,-3), Vector(-7,-5)])

        goal=Object([Vector(10,10), Vector(8,10), Vector(8,8), Vector(10,8)])

        #creation du sim
        env=Environment([drone1, drone2,drone3, drone4,drone5, drone6], [obj, obj1, obj2], goal)
        env.save("env_1")
    else:
        env=Environment()
        env.load("env_1")
        
    eventFenetre=EventDisplay()
    eventFenetre.coefTime=1/10

    simu=Simulator(env, eventFenetre)

    fenetre = Display(env, eventFenetre)
    
    simu.start()
    fenetre.run()
    simu.join()
    pygame.quit()
    

