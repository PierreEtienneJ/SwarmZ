from Vectors import Vector

class Object:
    """One object was represented by a list of Point : one Object is a polygone"""
    def __init__(self, L:list):
        """L was a list of Point and Point need to be in order"""
        self.list_Points=L
        self.center=Vector(0,0) #barycentre
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