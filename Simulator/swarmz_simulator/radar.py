
#from Objects import Object
from swarmz_simulator.collision import *
from swarmz_simulator.vector import Vector

import numpy as np
import math

class Radar:
    def __init__(self,ranges_, angles_:list):
        """Create one Radar

        Args:
            ranges_ (list or float): range of the radar by ray
            angles_ (list(rad)): angle of ray in rad
        """
        ##one ray with angle egual to zero do not work, so I replace it by 0.000000..0001
        for i in range(len(angles_)):
            if(angles_[i]==0):
                angles_[i]=1e-50

        if(type(ranges_)!=type([])):
            ranges_=[ranges_ for i in range(len(angles_))]

        self.rays=np.zeros((len(angles_,)))
        self.nb_rays=len(angles_)
        self.ranges_=ranges_   ##portées
        self.angles_=angles_   ##angle

        for i in range(self.nb_rays):
            self.rays[i]=ranges_[i]   ##ping
        self.ranges_=ranges_   ##portées
        self.angles_=angles_   ##angle

    def update(self, list_Objects:list=[], list_Drones:list=[])->None:
        """Update the Radar : with the two lists, this simulates a radar like a Lidar

        Args:
            list_Objects (list, Object): Object. Defaults to [].
            list_Drones (list, Drone): Drone. Defaults to [].
        """
        for I in range(self.nb_rays):
            tetha_i=self.angles_[I] #angle of Ith rays
            vdir=Vector(1,0)
            vdir.setCap(tetha_i)

            A=Vector(0,0)
            B=vdir.copy()
            B.setNorm(self.ranges_[I]) #radius of the Ith rays

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

class Lidar(Radar):
    def __init__(self, range_:float,nb_rays:int):
        self.deg_step=360/nb_rays
        self.rad_step=math.pi*2/nb_rays

        super().__init__(range_, [self.rad_step*i for i in range(nb_rays)])

    
        

