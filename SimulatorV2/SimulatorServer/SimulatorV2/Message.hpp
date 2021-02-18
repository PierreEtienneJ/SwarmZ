#ifndef MESSAGE_HPP
#define MESSAGE_HPP

#pragma once
class Message{
private:
	char* message;
	int payloadLength;
	char sum;
	int id_message;
public:
	Message(int id_message, char* TXmessage, int len); //creation d'un message à envoyer
	Message(char* RXmessage); //création d'un message recu

	int getId_message(void); //retourne l'ID du message
	virtual int getID_emetteur(void); //retourn l'ID de l'emetteur
	char* sendMessage(void); //retourne le message à envoyer
	char* getMessage(void); //retourne le message
	void calculSum(void); //calcul la sum des char
	int getPayloadLength(void); //retourne la taille du message
	bool goodMessage(void); //retourne true si le message est bon, false si la sum est pas bonne
};

class ClientWelcomeMessage : public Message {
private:
	int typeClient;
	int numero_essaim;
public:
	ClientWelcomeMessage(int typeClient, int numero_essaim);
};

#endif // !MESSAGE_H

