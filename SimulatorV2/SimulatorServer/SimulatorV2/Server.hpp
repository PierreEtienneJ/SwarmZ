#pragma once
#include "Sockets.hpp"
#include "Errors.hpp"
#include "Message.hpp"

#include <iostream>
#include <string>
#include <vector>

struct Client {
	SOCKET sckt;
	sockaddr_in addr;
};

class Server{
	private:
		int port;
		int maxClient;
		std::vector<Client> clients;
	protected:
		SOCKET socketServer;
	public:
		Server(int port);
		~Server();
		int start(bool cout);
		int run(bool cout);

};

