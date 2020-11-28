"""
L'environement correspond à l'ensemble des drones, des obstacles et des zones de scores 
qu'utilise le simulateur
"""

from Drones import Drone
from Objects import Object
from Vectors import Vector

import json

class Environment():
    def __init__(self, list_Drones=[], list_Objects=[]):
        self.drones=list_Drones
        self.objects=list_Objects

        self.nb_drones=len(list_Drones)
        self.nb_objects=len(list_Objects) 

    def addObject(self, listPoint):
        self.objects.append(Object(listPoint))
        self.nb_objects+=1

    def nearEnv(self, position, rayon)->tuple:
        drones=[]
        objs=[]
        for drone in self.drones:
            if(0<position.distance(drone.position)<rayon):
                drones.append(drone)
        
        for obj in self.objects:
            P=[]
            for point in obj.listPoint:
                if(position.distance(point)<rayon):
                    P.append(point)
            objs.append(Object(P))
        return (drones, objs)

    def save(self, nom="environement"):
        drones=[]

        for drone in self.drones:
            drones.append({"name":drone.name,
                            "position": {"x": drone.position.x, "y":drone.position.y},
                            "speed": {"vx": drone.vitesse.x, "vy":drone.vitesse.y},
                            "radius": drone.rayon,
                            "color": drone.color})
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
        file=open(nom+".json","w")
        json.dump(dic, file, indent=4)

    def load(self, name):
        if name[-5:]!=".json":
            name+=".json"

        try:
            f=open(name,'r')
            dic=json.load(f)
        except:
            print("Ouverture de fichier impossible, fichier non valide !")
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

                drones.append(Drone(position, vitesse, radius, name, color))
            
            objs=[]
            for obj in dic['objects']:
                points=[]
                for point in obj["points"]:
                    points.append(Vector(point["x"], point["y"]))

                objs.append(Object(points))
            
            self.objects=objs
            self.drones=drones
            self.nb_drones=len(drones)
            self.nb_objects=len(objs) 
        except:
            print("type de fichier non valide !")
            return None

