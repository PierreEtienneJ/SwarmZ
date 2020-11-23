import pygame
import math
import time
from simulateur import *
from Fenetre import *

if __name__ == '__main__':
    #creation des drones coordonnée, vitesse, rayon
    #at t=0
    #now, speed=cst
    drone1=Drone(Point(0,0),Point(0.5,0.5),0.1)
    drone2=Drone(Point(1,0),Point(-0.5,0),0.1)
    drone3=Drone(Point(0,1),Point(0.1,-0.5),0.1)

    #creation des obstacles, liste des coins
    obj=Object([Point(5,5), Point(3,5), Point(3,3), Point(5,3), Point(7,5)])
    obj1=Object([Point(-10,5), Point(-13,5), Point(-5,3)])

    #creation du simu
    simu=Simulator([drone1, drone2, drone3], [obj, obj1])

    #affichage : ecran
    pygame.init()
    size=(1080,720)
    ecran=pygame.display.set_mode(size, pygame.RESIZABLE)
    continuer = True
    
    #creation de la fenetre active
    fenetre = Fenetre(ecran, simu)

    

    while continuer:
        size=ecran.get_size()
        ecran.fill((25,25,250))
        police = pygame.font.Font(None,50)
        texte = police.render("Press key",True,pygame.Color("#FFFF00"))
        ecran.blit(texte, (size[0]/2, size[1]/3))
        for event in pygame.event.get(): #ecoute les events de touche
            #arrete si on appuie sur la croix ou sur echap
            if event.type == const.QUIT or (event.type == const.KEYDOWN and event.key == const.K_ESCAPE):
                continuer = 0
            if event.type == const.KEYDOWN: #appuyer sur une touche pour commencer
                fenetre.run()
                continuer=0

        pygame.display.flip()

    pygame.quit()

