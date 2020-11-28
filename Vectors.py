import math

class Vector:
    """This class was created for simplify all math operation with vector"""
    def __init__(self, x, y):
        self.x=x
        self.y=y
    
    def x_scalaire(self, a):
        """return the result of multiplication between this vector and the scalar a"""
        return Vector(self.x*a, self.y*a)
    
    def norm_2(self)->float:
        """return the norm 2 of this vector"""
        return math.sqrt(self.x*self.x+self.y*self.y)

    def cap(self)->float:
        """return angle between x and y"""
        return math.atan2(self.y, self.x)

    def distance(self, point):
        """return distance between two vector : this vector and one other"""
        return Vector(self.x-point.x,self.y-point.y).norm_2()

    def add(self, point):
        """addition one point"""
        return Vector(self.x+point.x,self.y+point.y)