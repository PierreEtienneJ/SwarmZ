import pygame
from simulateur import *
from pygame import locals as const
import time

class Fenetre:
    """this class use pygame to display the simulation"""
    def __init__(self, ecran:pygame.Surface, simu):
        """need one Surface and one simulation"""
        self.ecran=ecran
        self.simu=simu

        self.size=ecran.get_size()

        self.background=(20,20,150) #never use yet
        self.running = True

        #definition du zoom
        self.centre=Point(0,0)
        self.rayon=0
        self.zoom=1
        
        self.zoom_auto() #à # si vous voulez pas utiliser le zoom auto

        #sauvegarde des events 
        #pour déplacer le centre, clique gauche continue
        self.maintien_clique_gauche=False
        self.position_souris_avant=Point(0,0)

        self.maintien_clique_droit=False
        self.new_clique_Object=[]
        
    def zoom_auto(self):
        #recherche du barycentre des objets et des drones
        centre=Point(0,0)
        for drone in self.simu.drones:
            centre.x+=drone.position.x
            centre.y+=drone.position.y

        for obj in self.simu.objets:
            centre.x+=obj.center.x
            centre.y+=obj.center.y
        centre=centre.x_scalaire(1/(len(self.simu.objets)+ len(self.simu.drones)))

        self.centre=centre
        
        #recherche du points le plus loin du centre
        rayon=0
        for drone in self.simu.drones:
            if(self.centre.distance(drone.position)>rayon):
                rayon=self.centre.distance(drone.position)
        for obj in self.simu.objets:
            if(self.centre.distance(obj.center)>rayon):
                rayon=self.centre.distance(obj.center)
        
        self.rayon=rayon*1.5

        #def du zoom
        self.zoom=min(self.size)/2*1/self.rayon 
    
    def process_event(self, event:pygame.event):
        ##utilisation du zoom
        if(event.type == pygame.QUIT):
            self.running=False
        
        if(event.type == pygame.MOUSEBUTTONDOWN): #si on clique avec la souris
            if(event.button==1): #clique gauche
                self.maintien_clique_gauche=True
                x, y = event.pos #position de la souris
                self.position_souris_avant=Point(x,y) #sauvegarde

            if(event.button==1): #clique droit
                self.maintien_clique_droit=True
                x, y = event.pos #position de la souris
                
                #p_y=
                #self.new_clique_Object.append()

            if(event.button==4): #Molette souris haut
                self.zoom+=5   #on zoom


            if(event.button==5): #Molette souris bas
                self.zoom-=5   #on dezoom
                if(self.zoom<1):
                    self.zoom=1


        if(event.type == pygame.MOUSEBUTTONUP): # si on declique
            if(event.button==1): #clique gauche
                self.maintien_clique_gauche=False

        if(event.type==pygame.MOUSEMOTION): #si la souris bouge
            if(self.maintien_clique_gauche): #si le clique gauche est tjrs enfoncé
                x, y = event.pos #position souris
                delta=self.position_souris_avant.add(Point(x,y).x_scalaire(-1)) #delta=avant-après

                self.centre=self.centre.add(delta.x_scalaire(-1))  #centre=centre-delta
                self.position_souris_avant=Point(x,y)

    def decalage(self, a): #def décalage par rapport au centre de la fenètre
        x,y=a
        x=x+self.centre.x+self.size[0]/2
        y=-y+self.centre.y+self.size[1]/2
        return (x,y)

    def decalage_Point(self, p): #espèce de sur-définition
        return self.decalage((p.x, p.y))

    def update_screen(self):
        pygame.draw.rect(self.ecran, (20,20,100), (0,0)+self.size) #recrée un fond

        #dessine l'absice et l'ordonnée
        pygame.draw.line(self.ecran, (255,0,0),self.decalage((0,-1e4)), self.decalage((0, 1e4)))
        pygame.draw.line(self.ecran, (255,0,0),self.decalage((-1e4,0)), self.decalage((1e4, 0)))
        
        #dessine les obstacles
        for obj in self.simu.objets:
            pygame.draw.circle(self.ecran, (40,40,200), self.decalage_Point(obj.center.x_scalaire(self.zoom)), obj.rayon*self.zoom)
            
            points=obj.list_Points
            P=[]
            for point in points:
                P.append(self.decalage_Point(point.x_scalaire(self.zoom)))
            pygame.draw.polygon(self.ecran, (255,255,255), P,7)
        
        #draw all drones by circle 
        for drone in self.simu.drones:
            pygame.draw.circle(self.ecran, (255,100,50), self.decalage_Point(drone.position.x_scalaire(self.zoom)), drone.rayon*self.zoom)
    
    def run(self):
        t1=t0=time.time() #save time
        
        while(self.running): 
            for event in pygame.event.get(): #pécho les events
                self.process_event(event) #travail event
            self.update_screen() #modifie la fenètre
            pygame.display.flip() #update
            
            self.simu.update(time.time()-t0) #modifie la position des drones
            t0=time.time()
            self.size=self.ecran.get_size() #reupdate size

