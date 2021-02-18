#include "Sockets.hpp"
#include "TCPSocket.hpp"

#include <iostream>
//https://bousk.developpez.com/cours/reseau-c++/TCP/06-client-non-bloquant/
int main(){
	if (!Sockets::Start()){
		std::cout << "Error starting sockets : " << Sockets::GetError() << std::endl;
		return -1;
	}
	TCPSocket client;

	if (!client.Connect("127.0.0.1", 30000)){
		std::cout << "Impossible de se connecter au serveur [127.0.0.1:" << 30000 << "] : error n0" << Sockets::GetError() << std::endl;
	}
	else{
		std::cin.ignore();
		std::cout << "Connecte!" << std::endl;
		while(true){
			std::cout << "Entrez une phrase >";
			std::string phrase;
			std::getline(std::cin, phrase);
			if (client.Send(phrase.c_str(), phrase.length()) == SOCKET_ERROR){
				std::cout << "Erreur envoi : " << Sockets::GetError() << std::endl;
				break;
			}
			else{
				char buffer[512] = { 0 };
				int len = client.Receive(buffer, 512);
				if (len == SOCKET_ERROR){
					std::cout << "Erreur reception : " << Sockets::GetError() << std::endl;
					break;
				}
				else{
					std::string reply(buffer, len);
					std::cout << "Reponse du serveur : " << reply << std::endl;
				}
			}
		}
	}
	Sockets::Release();
	return 0;
}
