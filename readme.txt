To use this simulator, you need pygame and python3. 

Last update:
- new class :
	- Environment : now contains the drones and the
			save environment in .json self.save(name), self.load(name)
	- EventFenetre : allows a discussion between the window and the simulation

- change :
	- Simulator is inherited from threading.Thread
	- Fenetre : -accelerating of simulation with + or -
		    -run simulation with Enter
		    -pause : space
		    -quit : q or cross
		    -zoom : wheel 
		    -creating a barrier : -right click 
		                           -confirm : enter
		                           -annuler : escape
		                              
		                              
/!\ lack of confidence in collisions
