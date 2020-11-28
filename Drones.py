from Vectors import Vector

import random
import math
class Drone:
    """this class corespond to a drone, can simulate there deplacement not there AI"""
    def __init__(self, position:Vector, vitesse:Vector, rayon:float, name="", color=(-1,-1,-1)):
        self.position=position
        self.vitesse=vitesse
        self.rayon=rayon
        self.next_position=position
        self.next_vitesse=vitesse

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
        """if this drone was not colisioned, they can move"""
        self.position=self.next_position
        self.vitesse=self.next_vitesse

    def update(self, dt)->None:
        """calcul the next position with they speed and time"""
        self.next_position.x=self.position.x+self.vitesse.x_scalaire(dt).x
        self.next_position.y=self.position.y+self.vitesse.x_scalaire(dt).y
        self.next_vitesse=self.vitesse.x_scalaire(1+dt*0.01)

    def set_vitesse(self, new_vitesse:Vector)->None:
        """Can change speed"""
        self.next_vitesse=new_vitesse
    
    def get_position(self)->Vector:
        """return the position"""
        return self.position
    
    def get_rayon(self)->False:
        """return the radius"""
        return self.rayon

    def collision(self)->None:
        """Le drone s'occupe de sa collision"""
        prev_cap=self.vitesse.cap()
        delta=(2*random.random()-1)*math.pi/12
        

        self.next_vitesse=self.vitesse.setCap(self.vitesse.cap()+delta-math.pi)
        self.next_position=self.position

       # print("ancien cap : ",prev_cap*180/math.pi, "new cap: ",self.vitesse.cap()*180/math.pi)