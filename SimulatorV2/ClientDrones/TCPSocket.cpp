#include "TCPSocket.hpp"

#include <stdexcept>
#include <sstream>

TCPSocket::TCPSocket(){
	mSocket = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
	if (mSocket == INVALID_SOCKET)
	{
		std::ostringstream error;
		error << "Erreur initialisation socket (" << Sockets::GetError() << ")";
		throw std::runtime_error(error.str());
	}
}
TCPSocket::~TCPSocket(){
	Sockets::CloseSocket(mSocket);
}
bool TCPSocket::Connect(const std::string& ipaddress, unsigned short port){
	sockaddr_in server;
	inet_pton(AF_INET, ipaddress.c_str(), &server.sin_addr.s_addr);
	server.sin_family = AF_INET;
	server.sin_port = htons(port);
	return connect(mSocket, (const sockaddr*)&server, sizeof(server)) == 0;
}
int TCPSocket::Send(const char* data, unsigned int len){
	return send(mSocket, data, len, 0);
}
int TCPSocket::Receive(char* buffer, unsigned int len){
	return recv(mSocket, buffer, len, 0);
}