
# %%
import math
import threading
import time
import random
import statistics

from swarmz_simulator.vector import Vector
from swarmz_simulator.drone import Drone
from swarmz_simulator.display import Display, EventDisplay
from swarmz_simulator.object import Object
from swarmz_simulator.environment import Environment
import swarmz_simulator.collision as collision

class PhysicalSimulator(threading.Thread):
    def __init__(self, environment:"Environment", eventDisplay:"display.EventDisplay", **kwargs):
        """Simulator need one environment, he check colision between drone and drone and drones
        between drone and object"""
        threading.Thread.__init__(self)
        
        self.environment=environment
        self.eventDisplay=eventDisplay

        self.T=0

        self.dynamic_viscosity=kwargs.get("dynamic_viscosity",1e-3) #dynamic viscosity of water
        self.gravity=9.80665 #constant if gravity in earth
        
    def physicUpdate(self, dt:float, coefTime:float)->None:
        """
        Update drone Speed, Position and acceleration with a simulation of physic
        Arg : 
            dt:float, step time
        """
        for drone in self.environment.drones:
            drone.update(dt, coefTime=coefTime) #update Motor Vector
            
            K=0
            if(drone.pumpJet):
                if(-drone.maxOpeningAngle<drone.angularCommande<drone.maxOpeningAngle):
                    drone.motorPower.setCap(drone.angularCommande)
                elif(drone.angularCommande<0):
                    drone.motorPower.setCap(-drone.maxOpeningAngle)
                else:
                    drone.motorPower.setCap(drone.maxOpeningAngle)

            else:
                if(-drone.maxOpeningAngle<drone.angularCommande<drone.maxOpeningAngle):
                    K=drone.rudder_height*drone.rudder_width*math.sin(drone.angularCommande)

                elif(drone.angularCommande<0):
                    K=drone.rudder_height*drone.rudder_width*math.sin(-drone.maxOpeningAngle)
                else:
                    K=drone.rudder_height*drone.rudder_width*math.sin(drone.maxOpeningAngle)
                K=K*1e7
                

            ##we set new referential : xb, yb referential of boat  

            ##frottement fluid = -S mu * V**alpha
            local_speed=drone.speed.copy()
            local_speed.setCap(drone.speed.cap()-drone.angular)
            local_speed_n=local_speed.copy()
            local_speed_n.setNorm(1)
            Cx=1
            Cy=100000 #1e4
            
            fluidFriction_x=-1/2*drone.projected_area_x*self.dynamic_viscosity*abs(local_speed.x)**2*Cx
            fluidFriction_y=-1/2*drone.projected_area_y*self.dynamic_viscosity*abs(local_speed.y)**2*Cy

            if(local_speed.x<0):
                fluidFriction_x=-fluidFriction_x
            if(local_speed.y<0):
                fluidFriction_y=-fluidFriction_y

            drone.acceleration=Vector(fluidFriction_x,fluidFriction_y).add(drone.motorPower).x_scal(1/drone.mass)
            
            #self.angularAcceleration=(self.motorPower.y*self.positionOfRudder+K*self.positionOfRudder*self.dynamic_viscosity*self.speed.norm_2()**1)/self.moment_inertia
            moment_motor=drone.motorPower.y*drone.positionOfRudder*100
            moment_derive=-10*drone.positionOfRudder*fluidFriction_y
            drone.angularAcceleration=(moment_motor+moment_derive)/drone.moment_inertia

            drone.acceleration.setCap(drone.acceleration.cap()+drone.angular)

            drone.next_speed=drone.speed.add(drone.acceleration.x_scal(dt))
            
            if(drone.next_speed.norm_2()>drone.maxSpeed):
                drone.next_speed.setNorm(drone.maxSpeed)

            drone.angularSpeed=drone.angularAcceleration*dt
            drone.angular+=1/2*drone.angularAcceleration*dt
            

            drone.next_position.x=drone.position.x+1/2*drone.speed.x*dt*coefTime#+self.speed.x_scal(dt).x
            drone.next_position.y=drone.position.y+1/2*drone.speed.y*dt*coefTime
        
    def update(self, dt, coefTime)->list:
        """Here, we update next position for all drones with dt and check all collisions 
        dt was time betwenn now and previous position"""
        
        self.physicUpdate(dt, coefTime)
        
        collision_D_D=[]
        collision_D_Obj=[]
        
        for i in range(self.environment.nb_drones):
            #if(i!=self.environment.nb_drones-1): #si ce n'est pas le dernier drone
            #    for j in range(i+1,self.environment.nb_drones):
            #        if(self.collision_Drone_Drone(i,j)):
            #            collision_D_D.append(i)
            #            collision_D_D.append(j)

            for j in range(self.environment.nb_objects):
                if(self.collision_Drone_Objects(i,j)):
                    collision_D_Obj.append(i)

            if(self.environment.goal_has_def()):
                if self.droneGoal(i):
                    self.environment.drones[i].setGoal()

            ##on fixe l'environement autour du drone        
                       
      #  lead=random.randint(0,self.environment.nb_drones-1)
        for i in range(self.environment.nb_drones):
            if(i in collision_D_D or i in collision_D_Obj):
                self.environment.drones[i].collision()
            else:
                self.environment.drones[i].set_next()
                

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
        if(d==0):
            return False
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
                    
                    return True
                    ##on verifie si le drone ne s'éloigne pas de la ligne
                    #on calcul le point d'intersection entre V et (AB)
                    P=collision.intersection(A,Vector(A.x-B.x, A.y-B.y), self.environment.drones[i].next_position, self.environment.drones[i].next_speed)
                    if(P==None):
                        return False
                    else:
                        x=self.environment.drones[i].next_position.x
                        y=self.environment.drones[i].next_position.y
                        vx=self.environment.drones[i].next_speed.x
                        vy=self.environment.drones[i].next_speed.y
                        (a,b,c)=collision.droite(A,Vector(A.x-B.x, A.y-B.y))
                        

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
                if(self.eventDisplay.simulation):
                    self.eventDisplay.simulation=False
                    dt=time.time()-t1
                    self.update(self.eventDisplay.dt, self.eventDisplay.coefTime)
                    self.T+=self.eventDisplay.dt*self.eventDisplay.coefTime

            t1=time.time()

        self.stop()

    def stop(self):
        self.eventDisplay.stop=True


class RadarSimulator(threading.Thread):
    def __init__(self, environment, eventDisplay, **kwargs):
        threading.Thread.__init__(self)
        
        self.environment=environment
        self.eventDisplay=eventDisplay
        self.T=0
    def update(self, **kwargs):
        for i in range(self.environment.nb_drones):
            self.environment.drones[i].setEnvironment(self.environment.nearEnv(self.environment.drones[i].position, max(self.environment.drones[i].radar.ranges_)))
            ###in setEnvironment they are self.__updateRadar
            
    def run(self):
        t1=t0=time.time() #save time
        while(not self.eventDisplay.stop):
            if(not self.eventDisplay.pause):
                if(self.eventDisplay.radar):
                    self.eventDisplay.radar=False
                    dt=time.time()-t1
                    self.update(dt=self.eventDisplay.dt, coefTime=self.eventDisplay.coefTime)
                    self.T+=self.eventDisplay.dt*self.eventDisplay.coefTime
            t1=time.time()
