#include "Message.hpp"

Message::Message(int id_message, char* TXmessage, int len) { //creation d'un message à envoyer
	this->message = TXmessage;
	this->id_message = id_message;
	this->payloadLength = len;
	this->sum = 0;
	this->calculSum();
}
Message::Message(char* RXmessage) { //création d'un message recu

}
int Message::getId_message(void) { //retourne l'ID du message
	return this->id_message;
}
int Message::getID_emetteur(void) { //retourn l'ID de l'emetteur
	return -1;
}
char* Message::sendMessage(void) { //retourne le message à envoyer
	int len = 4 + this->payloadLength + 1 + 1;
	

}
char* Message::getMessage(void) { //retourne le message
}
void Message::calculSum(void) { //calcul la sum des char
	char sum = 0;
	sum += (char)'0xfe';
	sum += (char)this->payloadLength;
	for (int i = 0; i < this->payloadLength; i++) {
		sum += this->message[i];
	}
	this->sum = sum;
}
int Message::getPayloadLength(void) { //retourne la taille du message
}
bool Message::goodMessage(void) { //retourne true si le message est bon, false si la sum est pas bonne
}