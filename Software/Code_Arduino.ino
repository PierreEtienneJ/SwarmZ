 #include <Servo.h>
#include <HCSR04.h>
// SHEEE
Servo myservo; 
int pos = 0; 

const int trigPinGauche = 52;
const int echoPinGauche = 50;

const int trigPinDroit = 46;
const int echoPinDroit =44;

UltraSonicDistanceSensor distanceSensorDroit(trigPinDroit, echoPinDroit);
UltraSonicDistanceSensor distanceSensorGauche(trigPinGauche, echoPinGauche);
int mesuredisDroit=0;
int mesuredisGauche=0;



const int in1 = 2;      //Pont en H
const int in2 = 4;
const int enable = 3;

void setup() {
  
  myservo.attach(40);  // attaches the servo on pin 9 to the servo object
  myservo.write(100);


//Mcc
    pinMode(enable, OUTPUT);
    pinMode(in1, OUTPUT);
    pinMode(in2, OUTPUT);
    analogWrite(enable, 0);
    digitalWrite(in1, LOW);
    digitalWrite(in2, HIGH);
  
   Serial.begin(9600); 
}

void loop() {
  
 
mesuredisDroit=distanceSensorDroit.measureDistanceCm();
mesuredisGauche=distanceSensorGauche.measureDistanceCm();


if (mesuredisGauche<20 && mesuredisGauche>-1 )
  {
    
      myservo.write(80);             //tourne a droite
      analogWrite(enable, 50);       //vitesse reduite           
    
  }

else if (mesuredisDroit<20 && mesuredisDroit>-1 )
  {
    
      myservo.write(145);              //tourne a gauche 
      analogWrite(enable, 50);          // vitesse réduite         
    
  }
else 
  {
  myservo.write(115);                 //tuyère 0 degré
  analogWrite(enable, 255);           //Vitesse max PWM
  }

//Serial.println(mesuredisDroit);
//Serial.println(mesuredisGauche);
 //Serial.println(enable);
}
