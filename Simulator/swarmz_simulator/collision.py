import math
import cmath

from swarmz_simulator.vector import Vector


"""The set of the following functions aims at simplifying the calculation of collisions between two robots, a robot and an object...."""

def solv_polynome(a,b,c, complexe=True):
    """Solve the polynome's equation of degree 2 ax²+bx+c

    Args:
        a (float):
        b (float): 
        c (float): 
        complexe (bool) : if return cmath complexe if need

    Returns:
        tuple: x1,x2 solution of this equation
    """
    D=b**2-4*a*c 
    if(D<0):
        if(complexe):
            return (complex(-b/(2*a),math.sqrt(-D)/(2*a)), complex(-b/(2*a),-math.sqrt(-D)/(2*a)))
        else:
            return None
    if(a==0):
        if(b==0):
            return None
        else:
            return (c/b, c/b)
    
    else:
        return ((-b+math.sqrt(D))/(2*a), (-b-math.sqrt(D))/(2*a))
    
def Points_Intersection_DC(D, C, point=True):
    """Return all of 2 intersections point if the right D collied the circle C

    Args:
        D (tuple): D=(a,b) with y=ax+c
        C (tuple): C=(xc,yc,r) : the circle whith center (xc,yc) and radius r
        point (bool): if return type equal Vector
    
    Returns:
        Vector: P1,P2 all of solution 

    Explanation : 
        We know the equation of C : ((xc-x)²+(yc-y)²=r²) and the equation of D : y=a*x+b
    """
    (a,b)=D
    (xc,yc,r)=C

    #equation Ax²+Bx+C=0
    A1=(1+a**2)
    B1=2*(a*(b-yc)-xc)
    #C1=(b-yc)**2-r**2
    C1=xc**2+yc**2+b**2-2*b*yc-r**2
    ret=solv_polynome(A1,B1,C1, False)

    if(ret): #si il est bien défini
        (x1,x2)=ret
        y1=a*x1+b
        y2=a*x2+b
        #y1=math.sqrt(r**2-(x1-xc)**2)+yc
        #y2=math.sqrt(r**2-(x2-xc)**2)+yc
        if(point):
            return (Vector(x1,y1), Vector(x2,y2))
        else:
            return (x1,y1,x2,y2)


    else:
        return None

def Point_Intersection_DD(D1,D2):
    """Calcul the intersection point between D1 and D2

    Args:
        D1 (tuple): (a1,b1) y=a1*x+b1
        D2 (tuple): (a2,b2) y=a2*x+b2

    Returns:
        Vector:
    """
    (a1,b1)=D1
    (a2,b2)=D2

    if(a1==a2): #si les deux droites sont //
        return None

    x=(b2-b1)/(a1-a2)
    y=a1*x+b1

    return Vector(x,y)


#/!\ without verification
def Points_Intersection_CC(C1,C2, point=True):
    """Return all of 2 intersections point if the circle C1 collied with the circle C2

    Args:
        C1 (tuple): C1=(xc1,yc1,r1) : the circle whith center (xc1,yc1) and radius r1
        C2 (tuple): C2=(xc2,yc2,r2) : the circle whith center (xc2,yc2) and radius r2
    
    Returns:
        Vector or tuple: P1,P2 all of solution 

    Explanation : 
        We know the equation of C : ((xc-x)²+(yc-y)²=r²) 
    """
    (xc1,yc1,r1)=C1
    (xc2,yc2,r2)=C2
    
    if(xc1!=xc2):
        a=r2**2-r1**2-(xc1-xc2)**2-(yc1-yc2)**2
        b=-(yc1-yc2)/(xc1-xc2)
        c=a/(2*(xc1-xc2))

        A=(1+b**2)
        B=-2*c*b
        C=c**2
        r=solv_polynome(A,B,B,False)
        if(r):
            y1_,y2_=r
            x1_=c-y1_*b
            x2_=c-y2_*b

            x1=x1_-xc1
            x2=x2_-xc2
            y1=y1_-yc1
            y2=y2_-yc2
            
            if(point):
                return (Vector(x1,y1), Vector(x2,y2))
            else:
                return (x1,y1,x2,y2)


    elif(yc1!=yc2):
        a=r2**2-r1**2-(xc1-xc2)**2-(yc1-yc2)**2
        b=-(xc1-xc2)/(yc1-yc2)
        c=a/(2*(yc1-yc2))

        A=(1+b**2)
        B=-2*c*b
        C=c**2
        r=solv_polynome(A,B,B,False)
        if(r):
            x1_,x2_=r
            y1_=c-x1_*b
            y2_=c-x2_*b

            x1=x1_-xc1
            x2=x2_-xc2
            y1=y1_-yc1
            y2=y2_-yc2
            
            if(point):
                return (Vector(x1,y1), Vector(x2,y2))
            else:
                return (x1,y1,x2,y2)
        
    elif(r1!=r2):
        return None
    
    else:
        ##infinite de solution : on en sort 2
        x1=0
        y1=r1
        x2=r1
        y2=0
        if(point):
            return (Vector(x1,y1), Vector(x2,y2))
        else:
            return (x1,y1,x2,y2)
    
    return None

            

    
    
def droite(V,P):
    """return a,b ax+b=y la droite de vecteur directeur V passant par P"""
    #droite ax+by+c=0
    b=-V.x
    a=V.y
    c=-(a*P.x+b*P.y)

    if(b==0):
        b=1e-10

    return (-a/b,-c/b)

def Points_Intersection_SC(A,B,C):
    """Return all of 2 intersections point the circle C collied with AB

    Args:
        A : Vector
        B : Vector
        C : typle (xc,yc,r) circle radius : r and circle center in (xc,yc)
    
    Returns:
        list Vector: P1,P2 all of solution 
    """
    V=A.add(B.x_scal(-1))
    V.setNorm(1)
    r=Points_Intersection_DC(droite(V, A), C)
    P=[]
    if(r):
        (P1,P2)=r
        A_=Vector(min(A.x, B.x), min(A.y, B.y))
        B_=Vector(max(A.x, B.x), max(A.y, B.y))
        if(A_.x<P1.x<B_.x and A_.y<P1.y<B_.y): #si P1 est dans le carre de diagonale A_ B_
            P.append(P1)
        if(A_.x<P2.x<B_.x and A_.y<P2.y<B_.y): 
            P.append(P2)
        
        if(len(P)==0):
            return None
        else:
            return P

    else:
        return None

def Point_Intersection_SS(A,B,C,D):
    """Return intersection point if the segment AB collied with CD

    Args:
        A (Vector): [description]
        B (Vector): [description]
        C (Vector): [description]
        D (Vector): [description]
    """
    P=Point_Intersection_DD(droite(A.add(B.x_scal(-1)), A), droite(C.add(D.x_scal(-1)), C))
    if(P):
        A_=Vector(min(A.x, B.x), min(A.y, B.y))
        B_=Vector(max(A.x, B.x), max(A.y, B.y))
        C_=Vector(min(C.x, D.x), min(C.y, D.y))
        D_=Vector(max(C.x, D.x), max(C.y, D.y))

        if(A_.x<P.x<B_.x and A_.y<P.y<B_.y and C_.x<P.x<D_.x and C_.y<P.y<D_.y):
            return P
        else:
            return None
    else:
        return None

if __name__ == '__main__':
    A=Vector(-5,-5)
    B=Vector(5,5)

    C=Vector(5+2,-5+2)
    D=Vector(-5+2,5+2)

    P=Point_Intersection_SS(A,B,C,D)

    plt.plot([A.x, B.x], [A.y, B.y], 'r')
    plt.plot([C.x, D.x], [C.y, D.y], 'b')
    if(P):
        plt.plot([P.x], [P.y], 'ok')
    plt.show()

     