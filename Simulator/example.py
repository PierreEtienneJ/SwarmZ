import pygame
import math
import time
import threading
import statistics

from swarmz_simulator.vector import Vector
from swarmz_simulator.drone import Drone
from swarmz_simulator.simulator import Simulator
from swarmz_simulator.display import Display, EventDisplay
from swarmz_simulator.object import Object
from swarmz_simulator.environment import Environment

if __name__ == '__main__':
    #creation des drones coordonnée, vitesse, rayon
    #at t=0
    #now, speed=cst
    
    if(True):
        drone1=Drone(Vector(0,0),Vector(0.2,0),0.2)
        drone2=Drone(Vector(1,1),Vector(0.5,0.5),0.2)
        drone3=Drone(Vector(0,1),Vector(0,-0.5),0.2)
        drone4=Drone(Vector(1,1),Vector(0,0.5),0.2)
        drone5=Drone(Vector(0,0),Vector(0.5,0),0.2)
        drone6=Drone(Vector(2,1),Vector(0.5,0),0.2)
        

        #creation des obstacles, liste des coins
        obj=Object([Vector(5,5), Vector(3,5), Vector(3,3), Vector(5,3), Vector(7,5)])
        obj1=Object([Vector(-10,5), Vector(-13,5), Vector(-5,3)])
        obj2=Object([Vector(-5,-5), Vector(-3,-5), Vector(-3,-3), Vector(-5,-3), Vector(-7,-5)])

        goal=Object([Vector(10,10), Vector(8,10), Vector(8,8), Vector(10,8)])

        #creation du sim
        env=Environment([drone1, drone2,drone3, drone4,drone5, drone6], [obj, obj1, obj2], goal)
        env.save("env_1")
    else:
        env=Environment()
        env.load("env_1")

    eventFenetre=EventDisplay()
    eventFenetre.coefTime=1/1000

    simu=Simulator(env, eventFenetre)

    #affichage : ecran
    pygame.init()
    size=(1080,720) #taille par défaut
    ecran=pygame.display.set_mode(size, pygame.RESIZABLE) #taille modifiable

    #creation de la fenetre active
    fenetre = Display(ecran, env, eventFenetre)
    continuer = True
    while continuer:
        size=ecran.get_size()
        ecran.fill((25,25,250)) #fond d'écran bleu
        police = pygame.font.Font(None,50)
        texte = police.render("Press Enter",True,pygame.Color("#FFFF00")) #message texte
        a,b=texte.get_size()
        ecran.blit(texte, (size[0]/2-a/2, (size[1]-b)/3))

        for event in pygame.event.get(): #ecoute les events de touche
            #arrete si on appuie sur la croix ou sur echap
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                continuer = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN: #appuyer sur une touche pour commencer
                eventFenetre.stop=False
                continuer=False
        pygame.display.flip()
        
    if not eventFenetre.stop:
        simu.start()
        fenetre.run()

        pygame.quit()
        simu.join()

