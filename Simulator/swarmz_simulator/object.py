from swarmz_simulator.vector import Vector

class Object:
    """One object was represented by a list of Point : one Object is a polygone"""
    def __init__(self, L:list):
        """L was a list of Point and Point need to be in order"""
        self.list_Points=L
        self.center=Vector(0,0) #barycentre
        self.radius=0

        #calcul of barycentre
        if(len(self.list_Points)>0):
            for point in self.list_Points:
                self.center.x+=point.x
                self.center.y+=point.y
            
            self.center=self.center.x_scal(1/len(self.list_Points))
            
            #calcul of radius
            for point in self.list_Points:
                if(self.center.distance(point)>self.radius):
                    self.radius=self.center.distance(point)
            