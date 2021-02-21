#include "Server.hpp"


Server::Server(int port) {
	this->port = port;
	this->socketServer = -1;
	this->maxClient = 100;
}

Server::~Server() {
	Sockets::CloseSocket(this->socketServer);
	Sockets::Release();
}
int Server::start(bool cout=true) {
	if (!Sockets::Start()){
		if(cout)
			std::cout << "Erreur initialisation WinSock : " << Sockets::GetError();
		return -1;
	}

	this->socketServer = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);

	if (this->socketServer == INVALID_SOCKET){
		if (cout)
			std::cout << "Erreur initialisation socket : " << Sockets::GetError();
		return -2;
	}

	if (!Sockets::SetNonBlocking(this->socketServer)){
		if (cout)
			std::cout << "Erreur settings non-bloquant : " << Sockets::GetError();
		return -3;
	}

	sockaddr_in addr;
	addr.sin_addr.s_addr = INADDR_ANY; //inet_addr("127.0.0.1");//
	addr.sin_port = htons(30000);
	addr.sin_family = AF_INET;

	int res = bind(this->socketServer, (sockaddr*)&addr, sizeof(addr));
	if (res != 0){
		if (cout)
			std::cout << "Erreur bind : " << Sockets::GetError();
		return -3;
	}

	res = listen(this->socketServer, this->maxClient);
	if (res != 0){
		if (cout)
			std::cout << "Erreur listen : " << Sockets::GetError();
		return -4;
	}
	if (cout)
		std::cout << "Server demarre sur le port " << 30000 << std::endl;
	return 0;
};

int Server::run(bool cout=true) {
	while(true){
		sockaddr_in from = { 0 };
		socklen_t addrlen = sizeof(from);
		SOCKET newClientSocket = accept(this->socketServer, (SOCKADDR*)(&from), &addrlen);
		if (newClientSocket != INVALID_SOCKET){
			if (!Sockets::SetNonBlocking(newClientSocket)){
				if (cout)
					std::cout << "Erreur settings nouveau socket non-bloquant : " << Sockets::GetError() << std::endl;
				Sockets::CloseSocket(newClientSocket);
				continue;
			}
			Client newClient;
			newClient.sckt = newClientSocket;
			newClient.addr = from;
			const std::string clientAddress = Sockets::GetAddress(from);
			const unsigned short clientPort = ntohs(from.sin_port);
			if (cout)
				std::cout << "Connexion de " << clientAddress.c_str() << ":" << clientPort << std::endl;
			this->clients.push_back(newClient);
		}
		auto itClient = this->clients.cbegin();
		while (itClient != this->clients.cend()){
			const std::string clientAddress = Sockets::GetAddress(itClient->addr);
			const unsigned short clientPort = ntohs(itClient->addr.sin_port);
			char buffer[200] = { 0 };
			bool disconnect = false;
			int ret = recv(itClient->sckt, buffer, 199, 0);

			if (ret == 0){
				//!< Déconnecté
				disconnect = true;
			}
			if (ret == SOCKET_ERROR){
				int error = Sockets::GetError();
				if (error != static_cast<int>(Sockets::Errors::WOULDBLOCK)){
					disconnect = true;
					if (cout)
						std::cout << "SOCKET_ERROR WOULDBLOCK " << error << " de [" << clientAddress << ":" << clientPort << "]" << std::endl;
				}
				//!< il n'y avait juste rien à recevoir
			}
			std::string a(buffer, 200);
			bool c;
			bool print = false;
			for (int i = 0; i < 200; i++) {
				c = std::to_string(buffer[i]) == std::to_string(0);
				if (!c) {
					print = true;
				}
			}
			if (print && cout) {
				std::cout << "recive to [" << clientAddress << ":" << clientPort << "]" << a << std::endl;
			}

			ret = send(itClient->sckt, buffer, ret, 0);
			if (ret == 0 || ret == SOCKET_ERROR){
				//std::cout << "SOCKET_ERROR "<< ret << " de [" << clientAddress << ":" << clientPort << "]" << std::endl;
				//std::cout << "sending " << buffer << std::endl;
				//disconnect = true;
			}
			if (disconnect){
				if (cout)
					std::cout << "Deconnexion de [" << clientAddress << ":" << clientPort << "]" << std::endl;
				itClient = clients.erase(itClient);
			}
			else
				++itClient;
		}
	}
	return 0;
}