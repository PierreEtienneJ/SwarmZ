import math

class Vector:
    """This class was created for simplify all math operation with vector"""
    def __init__(self, x, y):
        self.x=x
        self.y=y
    
    def x_scal(self, a):
        """return the result of multiplication between this vector and the scalar a

        Args:
            a (float):

        Returns:
            Vector: a*Vector
        """
        return Vector(self.x*a, self.y*a)
    
    def norm_2(self)->float:
        """return the norm 2 of this vector : sqrt(x²+y²)
        Return:
            float: norm2 of self
        """
        return math.sqrt(self.x*self.x+self.y*self.y)

    def cap(self)->float:
        """
        Return:
            float: angle between x and y
        """
        return math.atan2(self.y, self.x)

    def distance(self, point:"Vector")->"Vector":
        """return distance between two vector : this vector and point
        Args:
            point (Vector): 

        Returns:
            Vector: 
        """
        return Vector(self.x-point.x,self.y-point.y).norm_2()

    def add(self, point:"Vector")->"Vector":
        """Return self+point
        Args:
            point (Vector)

        Returns:
            Vector
        """
        return Vector(self.x+point.x,self.y+point.y)

    def setCap(self, cap:float)->None:
        """set direction of self and keep the same norm
        Args:
            cap (float (rad)): 
        """
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

    
    def setNorm(self, norm:float)->None:
        """set the norm of self and keep the cap
        Args:
            norm (float): new norm of self
        """
        P=self.copy()
        if(self.norm_2()!=0):   
            P=P.x_scal(norm/self.norm_2())

        self.x=P.x
        self.y=P.y
    
    def copy(self)->"Vector":
        """return the copy of self
        Returns:
            Vector: same x and same y
        """
        return Vector(self.x, self.y)

if __name__ == '__main__':
    V=Vector(1,0)
    A=[]
    X=[]
    for angle in range(-360,360,1):
        V.setCap(angle*math.pi/180)
        A.append(V.cap()*180/math.pi) 
        X.append(angle)
    plt.plot(X,A)
    plt.show()