import pygame
from pygame import locals as const

import time
import threading
import statistics
from Environements import Environment
from Vectors import Vector

class Fenetre():
    """this class use pygame to display the simulation"""
    def __init__(self, ecran:pygame.Surface, environement:Environment, eventFenetre):
        threading.Thread.__init__(self)
        """need one Surface and one simulation"""
        self.ecran=ecran
        self.environement=environement
        self.eventFenetre=eventFenetre

        self.size=ecran.get_size()

        self.background=(20,20,150) #never use yet
        self.running = True

        #definition du zoom
        self.centre=Vector(0,0)
        self.rayon=0
        self.zoom=1
        
        self.zoom_auto() #à # si vous voulez pas utiliser le zoom auto
        
        self.clock= pygame.time.Clock()
        #sauvegarde des events 
        #pour déplacer le centre, clique gauche continue
        self.maintien_clique_gauche=False
        self.position_souris_avant=Vector(0,0)

        self.maintien_clique_droit=False
        self.new_clique_Object=[]
        
        self.pos_souris=[]
    
    def zoom_auto(self):
        #recherche du barycentre des objets et des drones
        centre=Vector(0,0)
        for drone in self.environement.drones:
            centre.x+=drone.position.x
            centre.y+=drone.position.y

        for obj in self.environement.objects:
            centre.x+=obj.center.x
            centre.y+=obj.center.y
        centre=centre.x_scalaire(1/(self.environement.nb_objects+ self.environement.nb_drones))

        self.centre=centre
        
        #recherche du points le plus loin du centre
        rayon=0
        for drone in self.environement.drones:
            if(self.centre.distance(drone.position)>rayon):
                rayon=self.centre.distance(drone.position)

        for obj in self.environement.objects:
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
                self.position_souris_avant=Vector(x,y) #sauvegarde

            if(event.button==3): #clique droit
                self.maintien_clique_droit=True
                x, y = event.pos #position de la souris
                #p_y=
                self.new_clique_Object.append(self.inv_decalagePoint((x,y)).x_scalaire(1/self.zoom))

            if(event.button==4): #Molette souris haut
                self.zoom+=5   #on zoom

            if(event.button==5): #Molette souris bas
                self.zoom-=5   #on dezoom
                if(self.zoom<1):
                    self.zoom=1

        if(event.type == pygame.MOUSEBUTTONUP): # si on declique
            if(event.button==1): #clique gauche
                self.maintien_clique_gauche=False
            
            if(event.button==3): #clique droit
                self.maintien_clique_droit=False

        if(event.type==pygame.MOUSEMOTION): #si la souris bouge
            self.pos_souris=event.pos
            if(self.maintien_clique_gauche): #si le clique gauche est tjrs enfoncé
                x, y = event.pos #position souris
                delta=self.position_souris_avant.add(Vector(x,y).x_scalaire(-1)) #delta=avant-après

                self.centre=self.centre.add(delta.x_scalaire(-1))  #centre=centre-delta
                self.position_souris_avant=Vector(x,y)

        if(event.type==pygame.KEYDOWN): #si on apuye sur une touche clavier
            if(event.key==pygame.K_SPACE): #espace
                if(self.eventFenetre.pause): #si on était en pause on enlève
                    self.eventFenetre.pause=False
                else: #si on était pas en pause on met pause
                    self.eventFenetre.pause=True
            
            if(event.key==const.K_q):
                self.stop()

            if(event.key==const.K_PLUS or event.key==const.K_KP_PLUS):
                self.eventFenetre.coefTime*=1.8

            if(event.key==const.K_MINUS or event.key==const.K_KP_MINUS):
                self.eventFenetre.coefTime*=1/2
            
            if(event.key == const.K_ESCAPE): #on appuye sur echap => annule le polygone
                self.new_clique_Object=[]
            if(event.key == const.K_RETURN): #sur enter on confirme le polygone
                if(len(self.new_clique_Object)>1):
                    self.environement.addObject(self.new_clique_Object)
                self.new_clique_Object=[]

        if(event.type == pygame.QUIT):
            self.stop()
            
    def decalage(self, a): #def décalage par rapport au centre de la fenètre
        x,y=a
        x=x+self.centre.x+self.size[0]/2
        y=-y+self.centre.y+self.size[1]/2
        return (x,y)
    
    def inv_decalage(self, a): #inversion du décalage par rapport au centre de la fenetre
        x,y=a
        x=x-(self.centre.x+self.size[0]/2)
        y=-y+self.centre.y+self.size[1]/2
        return (x,y)
    
    def inv_decalagePoint(self,a):
        (x,y)=self.inv_decalage(a)
        return Vector(x,y)

    def decalage_Point(self, p): #espèce de sur-définition
        return self.decalage((p.x, p.y))

    def update_screen(self):
        pygame.draw.rect(self.ecran, (20,20,100), (0,0)+self.size) #recrée un fond

        #dessine l'absice et l'ordonnée
        pygame.draw.line(self.ecran, (255,0,0),self.decalage((0,-1e4)), self.decalage((0, 1e4)))
        pygame.draw.line(self.ecran, (255,0,0),self.decalage((-1e4,0)), self.decalage((1e4, 0)))
        
        #dessine les obstacles
        for obj in self.environement.objects:
          #  pygame.draw.circle(self.ecran, (40,40,200,50), self.decalage_Point(obj.center.x_scalaire(self.zoom)), obj.rayon*self.zoom)
            
            points=obj.list_Points
            P=[]
            for point in points:
                P.append(self.decalage_Point(point.x_scalaire(self.zoom)))
            pygame.draw.polygon(self.ecran, (255,255,255), P,7)
        
        #draw all drones by circle 
        for drone in self.environement.drones:
            pygame.draw.circle(self.ecran, drone.color, self.decalage_Point(drone.position.x_scalaire(self.zoom)), drone.rayon*self.zoom)
            #drow speed vector
            pygame.draw.line(self.ecran, (0,0,0), self.decalage_Point(drone.position.x_scalaire(self.zoom)), 
                             self.decalage_Point(drone.position.add(drone.vitesse).x_scalaire(self.zoom)), 1)

        if(self.eventFenetre.pause):
            police = pygame.font.Font(None,60)
            texte = police.render("Pause",True,pygame.Color("#FFFF00"))
            a,b=texte.get_size()
            self.ecran.blit(texte, (self.size[0]/2-a/2, (self.size[1]-b)/3))

        #on dessine le polygone en cours
        if(len(self.new_clique_Object)>0):
            P=[]
            for point in self.new_clique_Object:
                P.append(self.decalage_Point(point.x_scalaire(self.zoom)))
            P.append(self.pos_souris)
            pygame.draw.lines(self.ecran, (255,255,255), False, P,2)

    def run(self):
        t1=t0=time.time() #save time
        T=[]
        while(not self.eventFenetre.stop): 
            for event in pygame.event.get(): #pécho les events
                self.process_event(event) #travail event
            self.update_screen() #modifie la fenètre
            pygame.display.flip() #update
            
            
            self.size=self.ecran.get_size() #reupdate size
            self.clock.tick(30)
            #time.sleep(max(1/30-time.time()-t0,0))
            self.eventFenetre.dt=time.time()-t0
            
            t0=time.time()

            if(len(T)==100):
                print('mean fps',1/statistics.mean(T))
                T=[]
            T.append(self.eventFenetre.dt)
    
    def stop(self):
        self.eventFenetre.stop=True
        


class EventFenetre():
    def __init__(self):
        #communication entre la fenetre et la simulation
        self.pause=False ##sert a mettre en pause la simulation
        self.stop=True #stop la simulation et la fenètre
        
        self.dt=0  #temps reel 
        self.coefTime=1/100  #ralentissement de la simulation