import time
import random

class Communication:
    def __init__(self,**kwargs):
        self.bufferRX=CircularBuffer(kwargs.get('size_bufferRX',128))
        self.bufferTX=CircularBuffer(kwargs.get('size_bufferTX',128))
        self.dt=0
        self.time=time.time()

        self.__maxRandomTime=kwargs.get('maxRandomTime',2)
        self.__minRandomTime=kwargs.get('minRandomTime',0.5)
        self.communicationRange=kwargs.get('communicationRange',100)

    def haveMsg(self):
        return not self.bufferRX.empty()

    def addRX(self, msg):
        self.bufferRX.add(msg)

    def getMsg(self):
        return self.bufferRX.pop()

    def waitingTX(self):
        return not self.bufferTX.empty()

    def addTX(self, msg):
        self.bufferTX.add(msg)

    def getSending(self):
        return self.bufferTX.pop()

    def send(self, canSend):
        if(canSend and self.waitingTX()):
           if (time.time()-self.time)>self.dt: 
               r=[]
               while not self.bufferTX.empty():
                    r.append(self.bufferTX.pop())
               return r
        elif(self.waitingTX() and not canSend):
           self.dt=((self.__maxRandomTime-self.__minRandomTime)*random.random()+self.__minRandomTime)
           self.time=time.time()
           return None
        return None

class CircularBuffer:
    def __init__(self, len):
        self.len=len
        self.tableau=[None for i in range(self.len)]
        self.readPosition=0
        self.writePosition=0

    def add(self,message):
        if(not self.full()):
            self.tableau[self.writePosition]=message
            self.writePosition=self.writePosition+1

            if(self.writePosition>=self.len):
                self.writePosition=0

    def pop(self):
        if(not self.empty()):
            ret=self.tableau[self.readPosition]
            self.tableau[self.readPosition]=None #à enlever 
            self.readPosition=self.readPosition+1

            if(self.readPosition>=self.len):
                self.readPosition=0

            return ret
    
    def monitoring(self):
        pass

    def full(self):
        if(self.readPosition>0):
            return (self.writePosition==self.readPosition-1)
        else:
            return (self.writePosition==self.len)
    
    def empty(self):
        return self.writePosition==self.readPosition
    
    def purge(self):
        self.readPosition=self.writePosition
