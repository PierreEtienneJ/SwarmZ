import socket
import sys
import time
from subprocess import *
HOST = "127.0.0.1"
PORT = 30000

socketClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
  socketClient.connect((HOST, PORT))
except socket.error:
  print("Serveur introuvable.")
  sys.exit()
print("Connexion établie avec le serveur.")
socketClient.send("hi".encode('utf-8'))

msgServeur = socketClient.recv(1024).decode("Utf8")
print(msgServeur)
    
while(True):
    socketClient.send("hi".encode('utf-8'))
    msgServeur = socketClient.recv(10).decode("Utf8")
    print(msgServeur)
    print("\n")
    time.sleep(1)
        #print(msgServeur)
        
class Message:
    def __init__(self, iDMessage, message):
        self.payload=0
        self.iDMessage=iDMessage
        self.message=message