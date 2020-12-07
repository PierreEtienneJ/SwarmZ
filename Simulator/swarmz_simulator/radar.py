
#from Objects import Object
from swarmz_simulator.collision import *
from swarmz_simulator.vector import Vector

import numpy as np
import math

class Radar:
    def __init__(self, range_:float,nb_rays:int):
        self.rays=range_*np.ones((nb_rays,))
        
        self.nb_rays=nb_rays
        self.range_=range_
        self.deg_step=360/nb_rays
        self.rad_step=math.pi*2/nb_rays

    def update(self, list_Objects:list=[], list_Drones:list=[])->None:
        """Update the Radar : with the two lists, this simulates a radar like a Lidar

        Args:
            list_Objects (list, Object): Object. Defaults to [].
            list_Drones (list, Drone): Drone. Defaults to [].
        """
        for I in range(self.nb_rays):
            tetha_i=I*self.rad_step
            vdir=Vector(1,0)
            vdir.setCap(tetha_i)

            A=Vector(0,0)
            B=vdir.copy()
            B.setNorm(self.range_)

            D0=droite(vdir, A)

            list_points=[B]
            
            for obj in list_Objects:
                if(len(obj.list_Points)>1):
                    C=obj.list_Points[0]
                    for i in range(1,len(obj.list_Points)):
                        D=obj.list_Points[i]
                        P=Point_Intersection_SS(A,B,C,D)
                        C=D
                        if(P):
                            list_points.append(P)
                    D=obj.list_Points[0]
                    P=Point_Intersection_SS(A,B,C,D)
                    if(P):
                        list_points.append(P)
            
            for drone in list_Drones:
                if(drone.position.norm_2()>0.1):
                    r=Points_Intersection_SC(A,B,(drone.position.x, drone.position.y, drone.radius))
                    if(r):
                        for p in r:
                            list_points.append(p)
            
            list_distance=[point.norm_2() for point in list_points]

            self.rays[I]=min(list_distance)
        

