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

    def setCap(self, cap):
        while(cap>math.pi):
            cap-=2*math.pi
        while(cap<-math.pi):
            cap+=2*math.pi
        n=self.norm_2()
        x2=n/math.sqrt(1+math.tan(cap)**2)
        if(math.pi/2<cap<3*math.pi/2 or -3*math.pi/2<cap<-math.pi/2):
            self.x=-x2
        else:
            self.x=x2
        self.y=math.tan(cap)*self.x
        
       
        

    
    def setNorm(self, norm):
        cap=self.cap()

     #   x=math.sqrt(norm**2-self.)

if __name__ == '__main__':
    V=Vector(1,0)
    V.setCap(170*math.pi/180)
    print("1",V.cap()*180/math.pi)

    V.setCap(V.cap()-math.pi)
    print("2",V.cap()*180/math.pi)
    #print(V.x, V.y)