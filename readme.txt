To use this simulator, you need pygame and python3. 

Dernière mise à jour :
- création de nouvelles classes :
	- Environment : contient désormais les drones et les objects
			permet l'enregistrement de l'environement sous forme de json self.save(name), self.load(name)
	- EventFenetre : permet une discussion entre la fenêtre et la simulation

- modification :
	- Simulator est maintenant une classe héritée de threading.Thread
	- Fenetre : -accélération de la simu avec + ou -
		    -lancer de la simulation avec Enter
		    -quitter la simulation avec q ou Escape ou la croix
		    
