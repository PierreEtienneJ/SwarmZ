import pygame
import math
import time
import threading
import statistics
import random
import os
import neat
import matplotlib.pyplot as plt
import pickle
from swarmz_simulator.vector import Vector
from swarmz_simulator.drone import Drone
from swarmz_simulator.simulator import PhysicalSimulator,RadarSimulator
from swarmz_simulator.display import Display, EventDisplay
from swarmz_simulator.object import Object
from swarmz_simulator.environment import Environment
from swarmz_simulator.radar import Radar, Lidar 

generation=0

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
        super().__init__(position, Vector(0,0), 0.2,name="R2D2",color=(50,50,100), **kwargs) #initialize the drone 
        self.radar=Radar(20,[0,math.pi/2,math.pi, -math.pi/2, math.pi/6, -math.pi/6]) #create specific Radar
        self.history["inputIA"]=[[0 for i in range(14)] for j in range(2)]
        self.__dt=0
        
    def IA(self,**kwargs):
        """create one specific IA
        all 10s, if the shortest ray are less than 2m, the drone turn of 90deg as the angle of this ray else, 
        he take cap of the goal whith a random 
        """
        dt=kwargs.get('dt', 1e-50)
        coefTime=kwargs.get('coefTime', 1)
        self.angularCommande=kwargs.get('angularCommande', 0)
        capLocalCommande=kwargs.get('capLocalCommande', self.capCommande-self.angular)
        self.__dt+=dt*coefTime
        
        if(self.__dt>1):
            self.__dt=0
            self.history["inputIA"].append(self.getInputIA(True))
        
        P=1
        I=0
        D=0
        self.angular=setRad(self.angular)
        self.capCommande=setRad(capLocalCommande+self.angular)
        
        err=self.angular-self.capCommande
        err=setRad(err)
            
            #commande of the ange of pumpjet 
        self.angularCommande=P*err+I*(self.PIDcap[1]+err*dt)+D*(err-self.PIDcap[2])/dt
        self.PIDcap[1]+=err*dt
        self.PIDcap[2]=err
            
        self.angularCommande=setRad(self.angularCommande)

        self.commandePower=20
        
        #print(self.angularCommande)
        
    def setCap(self, cap):
        cap=setRad(cap)
        self.capCommande=cap
        self.PIDcap=[0,0,0]
        
    def getInputIA(self, forHisto=False):
        L=[]
        for i in range(self.radar.nb_rays):
            L.append(self.radar.rays[i]/self.radar.ranges_[i])
            L.append(self.radar.angles_[i]/math.pi)
        
        if(self.goal!=None):
            goal=self.position.add(self.goal.x_scal(-1))
            goal.setCap(goal.cap()-self.getCap())
        else :
            goal=Vector(0,0)
        
        L.append(goal.cap()/math.pi)
        L.append(goal.norm_2())
        
        if(not forHisto):
            L=L+self.history["inputIA"][-1]
            
        return L
        
class MyDisplay(Display):
    def __init__(self,env, eventFenetre, **kwargs):
        super().__init__(env, eventFenetre) #initialize the drone 
        self.displayRadar=False
    
    def update_screen(self, **kwargs):
        super().update_screen(**kwargs)
        generation=kwargs.get('generation', None)
        if(generation):
            strGeneration=str(generation)
            if(len(strGeneration)<2):
                strGeneration="0"+strGeneration
            police = pygame.font.Font(None,40)
            texte = police.render("GEN: "+strGeneration,True,pygame.Color((200,200,200)))
            
            a,b=texte.get_size()
            c,d=self.size
            self.screen.blit(texte, ((c-a)/2, 0))
            
    def run(self, **kwargs):
        maxTime=kwargs.get("maxTime", 60)
        t1=t0=time.time() #save time
        T=[]
        while(not self.eventDisplay.stop):
            self.size=self.screen.get_size() #reupdate size
            self.clock.tick(60)
            #time.sleep(max(1/30-time.time()-t0,0))
            self.eventDisplay.setDt(time.time()-t0)

            if(not self.eventDisplay.pause):
                self.time+=self.eventDisplay.dt*self.eventDisplay.coefTime
                self.eventDisplay.simulation=True
                self.eventDisplay.radar=True

            
            self.update_screen(**kwargs) #modifie la fenètre
            pygame.display.flip() #update

            t0=time.time()
            
            if(len(T)>100):
                self.fps=1/statistics.mean(T)
                self.stdFps=statistics.stdev([1/e for e in T])
                T=[]
            T.append(self.eventDisplay.dt)
            
            for event in pygame.event.get(): #pécho les events
                self.process_event(event) #travail event
                
            if(self.time>maxTime):
                self.stop()
    
class MyPhysicalSimu(PhysicalSimulator):
    def __init__(self, env, eventDisplay, nets, ge):
        super().__init__(env, eventDisplay)
        self.nets=nets
        self.ge=ge
    
    def update(self, dt, coefTime):
        super().update(dt, coefTime)
        
        for i,drone in enumerate(self.environment.drones):
            output=self.nets[i].activate(drone.getInputIA())
            capLocalCommande=2*math.pi*output[0]

            drone.IA(capLocalCommande=capLocalCommande)
                
            self.ge[i].fitness=drone.fitness()+self.environment.fitnessSwarm()
                
    def ret(self):
        return (self.nets, self.ge)
                
def getInitialPosition(n, eps, a,center=Vector(0,0)):
    ###répartie en carré de n drones éloigner de eps 
    if((a/eps)**2<n):
        a=int(math.sqrt(n)*eps)
        
    positions=[]
    for i in range(a):
        for j in range(a):
            positions.append(Vector(i-a/2,j-a/2).x_scal(eps).add(center))
    
    random.shuffle(positions)
    return positions[:n]

def creatSomeObject(n, b, d, center=Vector(0,0), radius=5, rmax=10):
    """n : nombre d'object
    b ; nombre de branches, 
    d : distance entre 2 branches
    radius : ecart du centre"""
    l=2*int(rmax/d)
    pos=[[Vector(i-l/2,j-l/2).x_scal(d).add(center) for i in range(l)] for j in range(l)]

    Objects=[]
    while len(Objects)<n:
        i0,j0=random.randint(0,l-1),random.randint(0,l-1)
        P=[]
        if(pos[i0][j0].distance(center)>radius):
            P.append(pos[i0][j0])
            while len(P)<b:
                i1,j1=random.randint(-1,1), random.randint(-1,1)
                if(0<=i0+i1<l and 0<=j0+j1<l and (i1!=0 or j1!=0)):
                    if(pos[i0+i1][j0+j1].distance(center)>radius):
                        P.append(pos[i0+i1][j0+j1])
                        i0,j0=i0+i1,j0+j1
            Objects.append(Object(P))
            P=[]
    return Objects
    
def fitness(genomes, config):
    global generation
    generation+=1
    
    positions=getInitialPosition(len(genomes), 1.5, 5)
    nets=[]
    ge=[]
    drones=[]
    i=0
    for _,g in genomes :
        net=neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        drones.append(MyDrone(positions[i], ini_cap=(2*random.random()-1)*math.pi, pumpJet=True, maxPowerMotor=5,positionOfRudder=-0.2,
                              moment_inertia=0.2,maxOpeningAngle=20*math.pi/180))
        g.fitness=0
        ge.append(g)
        i+=1
    
    objects=creatSomeObject(50,6,1, Vector(0,0),10, 20)+[Object([Vector(-30, -30), Vector(-30, 30), Vector(30,30), Vector(30,-30)])]
        
    goal=Object([Vector(25,25), Vector(23,25), Vector(23,23), Vector(25,23)])
    
    env=Environment(drones, objects, goal)
    
    eventFenetre=EventDisplay()
    eventFenetre.coefTime=4
    physicalSimu=MyPhysicalSimu(env, eventFenetre, nets, ge)
    radarSim=RadarSimulator(env, eventFenetre)

    fenetre = MyDisplay(env, eventFenetre)
    
    physicalSimu.start()
    radarSim.start()
    fenetre.run(generation=generation, maxTime=120)
    
    nets, ge=physicalSimu.ret()
    physicalSimu.join()
    radarSim.join()
    
def replay_genome(config_path, genome_path="winner.pkl", nb=20):
    # Load requried NEAT config
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, 
                                neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)

    # Unpickle saved winner
    with open(genome_path, "rb") as f:
        genome = pickle.load(f)

    # Convert loaded genome into required data structure
    genomes = [(1, genome) for i in range(nb)]

    # Call game with only the loaded genome
    fitness(genomes, config)


def run(config_path):
    config=neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, 
                              neat.DefaultStagnation, config_path)
    
    population=neat.Population(config)
    
    population.add_reporter(neat.StdOutReporter(True))
    
    stats=neat.StatisticsReporter()
    
    population.add_reporter(stats)
    
    winner=population.run(fitness,40)
    
    with open("winner.pkl", "wb") as f:
        pickle.dump(winner, f)
        f.close()
if __name__ == '__main__':
    local_dir=os.path.dirname(__file__)
    config_path=os.path.join(local_dir, "config_NEAT.txt")
    run(config_path)
    #replay_genome(config_path,genome_path="winner.pkl", nb=20)
    

