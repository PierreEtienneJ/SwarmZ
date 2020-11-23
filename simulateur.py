
# %%
import math
class Simulator:
    def __init__(self, drones:list, objets:list):
        """Simulator need one Drone's list and one object's list, he check colision between drone and drone and drones
        between drone and object"""

        self.drones=drones
        self.objets=objets
        self.nb_drones=len(self.drones)

    def update(self, dt)->list:
        """Here, we update next position for all drones with dt and check all collisions 
        dt was time betwenn now and previous position"""
        for i in range(self.nb_drones):
            self.drones[i].update(dt)
        
        collision_D_D=[]
        collision_D_Obj=[]
        for i in range(self.nb_drones-1):
            for j in range(i+1,self.nb_drones):
                if(self.collision_Drone_Drone(i,j)):
                    collision_D_D.append(i)
                    collision_D_D.append(j)

            for j in range(len(self.objets)):
                if(self.collision_Drone_Objets(i,j)):
                    collision_D_Obj.append(i)

        for i in range(self.nb_drones):
            if(i in collision_D_D or i in collision_D_Obj):
                self.drones[i].vitesse=Point(0,0)
            else:
                self.drones[i].set_next()

        return (collision_D_D, collision_D_Obj)

    def collision_Drone_Drone(self, i:int,j:int):
        """Here we check colision between two drones : drone i and drone j in the list of drones"""
        next_distance=self.drones[i].next_position.distance(self.drones[j].next_position)

        if(next_distance<self.drones[i].get_rayon()+self.drones[j].get_rayon()):
            return True
        else:
            return False

    def collision_Drone_Objets(self,i:int, j:int):
        """Here we check collision betwen drone i in the list of drone and the object j in the list of objects
        2 step :- we check collision between drone and object considered as a circle 
                - they are collision, we check more precisely if they are a collision. 
                """
        distance=self.drones[i].next_position.distance(self.objets[j].center)

        if(distance<self.drones[i].get_rayon()+self.objets[j].rayon):
            return True
        else:
            return False

class Point:
    """This class was created for simplify all math operation with vector"""
    def __init__(self, x, y):
        self.x=x
        self.y=y
    
    def x_scalaire(self, a):
        """return the result of multiplication between this vector and the scalar a"""
        return Point(self.x*a, self.y*a)
    
    def norm_2(self)->float:
        """return the norm 2 of this vector"""
        return math.sqrt(self.x*self.x+self.y*self.y)

    def cap(self)->float:
        """return angle between x and y"""
        return math.atan2(self.y, self.x)

    def distance(self, point):
        """return distance between two vector : this vector and one other"""
        return Point(self.x-point.x,self.y-point.y).norm_2()

    def add(self, point):
        """addition one point"""
        return Point(self.x+point.x,self.y+point.y)

class Drone:
    """this class corespond to a drone, can simulate there deplacement not there AI"""
    def __init__(self, position:Point, vitesse:Point, rayon:float):
        self.position=position
        self.vitesse=vitesse
        self.rayon=rayon
        self.next_position=position
        self.next_vitesse=vitesse
    
    def set_next(self):
        """if this drone was not colisioned, they can move"""
        self.position=self.next_position
        self.vitesse=self.next_vitesse

    def update(self, dt)->None:
        """calcul the next position with they speed and time"""
        self.next_position.x=self.position.x+self.vitesse.x_scalaire(dt).x
        self.next_position.y=self.position.y+self.vitesse.x_scalaire(dt).y

    def set_vitesse(self, new_vitesse:Point)->None:
        """Can change speed"""
        self.next_vitesse=new_vitesse
    
    def get_position(self)->Point:
        """return the position"""
        return self.position
    
    def get_rayon(self)->False:
        """return the radius"""
        return self.rayon
    
class Object:
    """One object was represented by a list of Point : one Object is a polygone"""
    def __init__(self, L:list):
        """L was a list of Point and Point need to be in order"""
        self.list_Points=L
        self.center=Point(0,0) #barycentre
        self.rayon=0 #cercle inscrit

        #calcul du barycentre
        for point in self.list_Points:
            self.center.x+=point.x
            self.center.y+=point.y
        
        self.center=self.center.x_scalaire(1/len(self.list_Points))
        
        #calcul du rayon
        for point in self.list_Points:
            if(self.center.distance(point)>self.rayon):
                self.rayon=self.center.distance(point)


# %%
