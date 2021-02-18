#pragma once

#ifdef _WIN32
#include <WinSock2.h>
//#include <winsock.h>
#include <windows.h>
#if !defined(_MSC_VER)
#include <WS2tcpip.h>
#define inet_ntop(FAMILY, PTR_STRUCT_SOCKADDR, BUFFER, BUFFER_LENGTH) strncpy(BUFFER, inet_ntoa(*static_cast<struct in_addr*>((PTR_STRUCT_SOCKADDR))), BUFFER_LENGTH)
#define inet_pton(FAMILY, IP, PTR_STRUCT_SOCKADDR) (*(PTR_STRUCT_SOCKADDR)) = inet_addr((IP))
#elif _MSC_VER >= 1800
#include <WS2tcpip.h>
#else
#define inet_ntop(FAMILY, PTR_STRUCT_SOCKADDR, BUFFER, BUFFER_LENGTH) strncpy(BUFFER, inet_ntoa(*static_cast<struct in_addr*>((PTR_STRUCT_SOCKADDR))), BUFFER_LENGTH)
#define inet_pton(FAMILY, IP, PTR_STRUCT_SOCKADDR) (*(PTR_STRUCT_SOCKADDR)) = inet_addr((IP))
typedef int socklen_t;
#endif
#ifdef _MSC_VER
#if _WIN32_WINNT >= _WIN32_WINNT_WINBLUE
//!< Win8.1 & higher
#pragma comment(lib, "Ws2_32.lib")
#else
#pragma comment(lib, "wsock32.lib")
#endif
#endif

#else
#include <sys/socket.h>
#include <netinet/in.h> // sockaddr_in, IPPROTO_TCP
#include <arpa/inet.h> // hton*, ntoh*, inet_addr
#include <unistd.h>  // close
#include <cerrno> // errno
#define SOCKET int
#define INVALID_SOCKET ((int)-1)
#define SOCKET_ERROR (int(-1))
#endif

#include <string>

#include <iostream>

#define BUFFERSIZE 512
#define PROTOPORT 5193 // Default port number


void ClearWinSock() {
#if defined WIN32
	WSACleanup();
#endif
}


void ErrorHandler(char* errorMessage) {
	std::cout << errorMessage << std::endl;
}

typedef struct Boat {
	char name[30];
	int size[3];
}Boat;

int main(void) {
#if defined WIN32
	WSADATA wsaData;
	int iResult = WSAStartup(MAKEWORD(2, 2), &wsaData);
	if (iResult != 0) {
		std::cout << "error at WSASturtup\n";
		return 0;
	}
#endif
	sockaddr_in server;
	inet_pton(AF_INET, "127.0.0.1", &server.sin_addr.s_addr);
	server.sin_family = AF_INET;
	server.sin_port = htons(9999);
	SOCKET client = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
	Sockets::SetNonBlocking(client);
	if (connect(client, reinterpret_cast<const sockaddr*>(&server), sizeof(server)) != 0)
	{
		int error = Sockets::GetError();
		if (error != static_cast<int>(Sockets::Errors::INPROGRESS) && error != static_cast<int>(Sockets::Errors::WOULDBLOCK))
		{
			std::cout << "Erreur connect : " << error << std::endl;
			return -2;
		}
	}
	bool connected = false;
	pollfd fd = { 0 };
	fd.fd = client;
	fd.events = POLLOUT;
	while (true)
	{
		int ret = poll(&fd, 1, 0);
		if (ret == -1)
		{
			std::cout << "Erreur poll : " << Sockets::GetError() << std::endl;
			break;
		}
		else if (ret > 0)
		{
			if (fd.revents & POLLOUT)
			{
				connected = true;
				std::cout << "Socket connecte" << std::endl;
				break;
			}
			else if (fd.revents & (POLLHUP | POLLNVAL))
			{
				std::cout << "Socket deconnecte" << std::endl;
				break;
			}
			else if (fd.revents & POLLERR)
			{
				socklen_t err;
				int errsize = sizeof(err);
				if (getsockopt(client, SOL_SOCKET, SO_ERROR, reinterpret_cast<char*>(&err), &errsize) != 0)
				{
					std::cout << "Impossible de determiner l'erreur : " << Sockets::GetError() << std::endl;
				}
				else if (err != 0)
					std::cout << "Erreur : " << err << std::endl;
				break;
			}
		}
	}

	if (connected)
	{
		//!< connexion établie avec succès
	}
	closesocket(socketClient);
	ClearWinSock();
	return 0;
}