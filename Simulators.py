
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
        
        for i in range(self.environement.nb_drones):
            if(i!=self.environement.nb_drones-1): #si ce n'est pas le dernier drone
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
    
        if(next_distance<=(self.environement.drones[i].get_rayon()+self.environement.drones[j].get_rayon())):
            x=self.environement.drones[i].next_vitesse.x*self.environement.drones[j].next_vitesse.x
            y=self.environement.drones[i].next_vitesse.y*self.environement.drones[j].next_vitesse.y

            if(x<0 or y<0):
                        ##si les vitesses ne convergent pas ni quelles sont dans le meme sens
                return False
            else:
                return True
        else:
            return False

    def __collisionDroiteCercle(self,A,B,P, r):
        """On regarde si il ya collision entre le cercle de rayon r et de centre P avec le segment A,B"""
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
        distance=self.environement.drones[i].next_position.distance(self.environement.objects[j].center)

        if(distance<self.environement.drones[i].get_rayon()+self.environement.objects[j].rayon):
            """si il y a collision entre les cercles du drone et de l'objet, on regarde si il y a une vrai collision"""
            #//https://openclassrooms.com/fr/courses/1374826-theorie-des-collisions/1375352-formes-plus-complexes page fermé :/

            A=self.environement.objects[j].list_Points[0]
            for l in range(1,len(self.environement.objects[j].list_Points)):
                B=self.environement.objects[j].list_Points[l]
                if(self.__collisionDroiteCercle(A,B,self.environement.drones[i].next_position, self.environement.drones[i].rayon)): #si le robot colisionne avec la ligne
                    ##on verifie si le drone ne s'éloigne pas de la ligne
                    return True
                    #on calcul le point d'intersection entre V et (AB)
                    P=intersection(A,Vector(A.x-B.x, A.y-B.y), self.environement.drones[i].next_position, self.environement.drones[i].next_vitesse)
                    if(P==None):
                        return False
                    else:
                        x=self.environement.drones[i].next_position.x
                        y=self.environement.drones[i].next_position.y
                        vx=self.environement.drones[i].next_vitesse.x
                        vy=self.environement.drones[i].next_vitesse.y
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
            return self.__collisionDroiteCercle(A,self.environement.objects[j].list_Points[0],self.environement.drones[i].next_position, self.environement.drones[i].rayon)
                
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


def intersection(A, VA, B, VB):
        (a1,b1,c1)=droite(VA,A)
        (a2,b2,c2)=droite(VB,B)

        if((b1==0 and b2==0) or a1==a2): #si les deux droites sont vertical et/ou //
            return None
        
        if(b1==0):
            x=A.x
            d2,e2=-a2/b2,-c2/b2
            y=d2*x+e2
            return Vector(x,y)

        else:
            d1,e1=-a1/b1,-c1/b1
        
        if(b2==0):
            x=B.x
            d1,e1=-a1/b1,-c1/b1
            y=d1*x+e1
            return Vector(x,y)
        else:
            d2,e2=-a2/b2,-c2/b2

        if(d1==d2):
            return None

        x=(e2-e1)/(d1-d2)
        y=d2*x+e2
        return Vector(x,y)

def droite(V,P):
    """return a,b,c ax+by+c=0 la droite de vecteur directeur V passant par P"""
    b=-V.x
    a=V.y
    c=-(a*P.x+b*P.y)
    return (a,b,c)

# %%
