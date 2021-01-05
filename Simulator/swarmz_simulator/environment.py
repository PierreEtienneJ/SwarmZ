"""
L'environement correspond à l'ensemble des drones, des obstacles et des zones de scores 
qu'utilise le simulateur
"""

import swarmz_simulator
from swarmz_simulator.vector import Vector
from swarmz_simulator.drone import Drone
from swarmz_simulator.object import Object

import json

class Environment():
    def __init__(self, list_Drones:list=[], list_Objects:list=[], goal=None):
        self.drones=list_Drones
        self.objects=list_Objects
        self.goal=goal
        self.nb_drones=len(list_Drones)
        self.nb_objects=len(list_Objects) 
        
        self.__names=[]
        self.renameDrone()
        
    def addObject(self, listPoint:list)->None:
        """creat and add one Object by list of Vector
        Args:
            listPoint (list(Vector)): list of Vector
        """
        self.objects.append(Object(listPoint))
        self.nb_objects+=1
    
    def add(self, something):
        if(isinstance(something,swarmz_simulator.drone.Drone)):
            self.drones.append(something)
            self.nb_drones+=1
            self.renameDrone()
        elif(isinstance(something,swarmz_simulator.object.Object)):
            self.objects.append(something)
            self.nb_objects+=1
        else:
            print("Error")

    def nearEnv(self, position:"Vector", radius:float)->tuple:
        """return all of Object and all of drone in the circle of the center position and the radius 
        Args:
            listPoint (list(Vector)): list of Vector
        Return :
            tuple (list(Drone), list(Object), goal) : order by distance
        """
        drones=[]
        objs=self.objects
        for drone in self.drones:
            d=position.distance(drone.position)
            if(0<d+drone.radius<radius):
                drones.append([d,drone])
                
        """
        for obj in self.objects:
            P=[]
            D=[]
            for point in obj.list_Points:
                d=position.distance(point)
                D.append(d)
              #  if(d<rayon):
                P.append(point)
            objs.append([min(D),Object(P)])"""
        
        D=sorted(drones, key=lambda x:x[0])
        #O= sorted(objs, key=lambda x:x[0])
        drones=[D[i][1] for i in range(len(D))]
        #objs=[O[i][1] for i in range(len(O))]

        if(self.goal_has_def()):
            return (drones, objs, self.goal.center)
        return (drones, objs, None) 

    def goal_has_def(self):
        return type(self.goal)==type(Object([]))

    def save(self, name:str="environment"):
        """create one file name as nom, with all of this environment

        Args:
            nom (str): name of the file without extension
        """
        if name[-5:]!=".json":
            name+=".json"
        drones=[]

        for drone in self.drones:
            drones.append({"name":drone.name,
                            "position": {"x": drone.position.x, "y":drone.position.y},
                            "speed": {"vx": drone.speed.x, "vy":drone.speed.y},
                            "radius": drone.radius,
                            "color": drone.color, 
                            "cap":drone.getCap()})
        objs=[]
        i=0
        for obj in self.objects:
            L=[]
            for point in obj.list_Points:
                L.append({"x":point.x, "y":point.y})
            objs.append({"name": "object_"+str(i),
                        "points":L})
            i+=1

        dic={
            "drones":drones,
            "objects":objs}

        if(self.goal_has_def()):
            L=[]
            for point in self.goal.list_Points:
                L.append({"x":point.x, "y":point.y})

            dic["goal"]={"points": L}

        file=open(name,"w")
        json.dump(dic, file, indent=4)

    def load(self, name:str, class_drone=Drone):
        """load a save of environment with json compatible

        Args:
            name (str): name of the folder

        Returns:
            [type]: [description]
        """
        if name[-5:]!=".json":
            name+=".json"

        try:
            f=open(name,'r')
            dic=json.load(f)
        except:
            print("Unable to open file, invalid file!")
            print("nom : ", name)
            return None

        try:
            drones=[]
            for drone in dic['drones']:
                position=Vector(drone["position"]["x"],drone["position"]["y"])
                vitesse=Vector(drone["speed"]["vx"],drone["speed"]["vy"])
                radius=drone["radius"]
                color=(drone["color"][0],drone["color"][1],drone["color"][2])
                name=drone["name"]
                cap=drone['cap']

                drones.append(class_drone(position, vitesse, radius, name, color, ini_cap=cap))
            
            objs=[]
            for obj in dic['objects']:
                points=[]
                for point in obj["points"]:
                    points.append(Vector(point["x"], point["y"]))

                objs.append(Object(points))
            
            try:
                points=[]
                for point in dic['goal']["points"]:
                    points.append(Vector(point["x"], point["y"]))
                self.goal=Object(points)

            except :
                self.goal=None
            
            self.objects=objs
            self.drones=drones
            self.nb_drones=len(drones)
            self.nb_objects=len(objs) 
            self.renameDrone()
        except:
            print("invalid file type!")
            return None

    def SwarmCaracteristics(self):
        if(self.nb_drones==0):
            return (Vector(0,0), 0, 0,0)
        
        center=Vector(0,0)
        for drone in self.drones:
            center=center.add(drone.position)

        center=center.x_scal(1/self.nb_drones)
        
        radius=0
        finisher=0
        for drone in self.drones:
            distance=center.distance(drone.position)
            if(drone.arrive):
                finisher+=1
            if(distance>radius):
                radius=distance
        
        density=math.pi*radius**2/self.nb_drones
        fiisher=finisher/self.nb_drones
        
        return (center, radius, density, finisher)
    
    def fitnessSwarm(self):
        if(self.nb_drones==0):
            return 0
        return 0

    def regName(self, string):
        j=len(string)-1
        while j>0:
            if(string[j]=='_'):
                break
            j-=1
        if(j==0):
            return string
        return string[:j]
        
    def renameDrone(self):
        self.__names=[self.regName(drone.name) for drone in self.drones]
        for i,drone in enumerate(self.drones):
            j=0
            name=self.__names[i]
            while(self.__names.count(name)>1):
                name=self.__names[i]+"_"+str(j)
                j+=1
            self.__names[i]=name
            drone.name=name