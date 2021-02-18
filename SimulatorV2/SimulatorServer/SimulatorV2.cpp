//FedericoPonzi

#if defined WIN32
#include <winsock.h>
#include <windows.h>
//#include <WS2tcpip.h>


#else

#define closesocket close
#include <sys/socket.h>
#include <arpa/inet.h>
#include <unistd.h>

#endif

#pragma once

#ifdef _WIN32
//#include <WinSock2.h>
#else
#include <cerrno>
#define SOCKET int
#define INVALID_SOCKET ((int)-1)
#define SOCKET_ERROR (int(-1))
#endif


#include <stdio.h>
#include <string>
#include <map>
#include <iostream>
#include <vector>

#define BUFFERSIZE 512
#define PROTOPORT 5193 // Default port number
# pragma comment(lib,"ws2_32.lib") //Winsock Library

void ClearWinSock() {
#if defined WIN32
	WSACleanup();
#endif
}


void ErrorHandler(char* errorMessage) {
	std::cout << errorMessage << std::endl;
}


int main(void) {
	#if defined WIN32
		WSADATA wsaData;
		int iResult = WSAStartup(MAKEWORD(2, 2), &wsaData);
		if (iResult != 0) {
			std::cout << "error at WSASturtup\n";
			return 0;
		}
	#endif

	// Socket creation
	int socketServer;
	socketServer = socket(AF_INET, SOCK_STREAM,0 ); //AF_INET or PF_INET //IPPROTO_TCP
	if (socketServer < 0) {
		char text[] = "socket creation failed.\n";
		ErrorHandler(text);
		closesocket(socketServer);
		ClearWinSock();
		return 0;
	}

#if defined WIN32
	unsigned long mode = 1;
	ioctlsocket(socketServer, FIONBIO, &mode);
#else
	fcntl(socketServer, F_SETFL, O_NONBLOCK);
#endif
	// Server address construction
	struct sockaddr_in addrServeur;
	//memset(&sad, 0, sizeof(sad));
	addrServeur.sin_addr.s_addr= inet_addr("127.0.0.1"); // server IP
	addrServeur.sin_family = AF_INET;
	addrServeur.sin_port = htons(30000); // Server port
	bind(socketServer, (const struct sockaddr*)&addrServeur, sizeof(addrServeur));

	// Connection to the server
	if (socketServer < 0) {
		char text[] = "Failed to connect.\n";
		ErrorHandler(text);
		closesocket(socketServer);
		ClearWinSock();
		return 0;
	}


	listen(socketServer, 10);

	struct sockaddr_in addrClient;
	//socklen_t csize = sizeof(addrClient);
	int csize = sizeof(addrClient);
	int socketClient;
	std::cout << "Waiting client..." << std::endl;
	do {
		socketClient = accept(socketServer, (struct sockaddr *)&addrClient, &csize);
	} while (socketClient<0);
	std::cout << "Client accepted :"+std::to_string(socketClient)  << std::endl;

	char buffer[] = "bonjour";
		
	Sleep(5000);
	int status=send(socketClient, buffer, sizeof(buffer), 0);
	if (status < 0) {
		std::cout << "Error to send" << std::endl;
	}
	else {
		std::cout << "sended" << std::endl;
		std::cout << buffer << std::endl;
	}
	char bufferRX[BUFFERSIZE];
	recv(socketClient, bufferRX, BUFFERSIZE, 0);

	std::cout << (std::string)bufferRX << std::endl;
	/*
	char inputString[] = "prova"; // String to send
	int stringLen = strlen(inputString);
	send(socketServer, inputString, stringLen, 0);


	int bytesRcvd;
	int totalBytesRcvd = 0;
	char buf[BUFFERSIZE]; // buffer for data from the server
	printf("Received: "); // Setup to print the echoed string

	while (totalBytesRcvd < stringLen) {
		if ((bytesRcvd = recv(socketServer, buf, BUFFERSIZE - 1, 0)) <= 0) {
			char text[] = "recv() failed or connection closed prematurely";
			ErrorHandler(text);
			closesocket(socketServer);
			ClearWinSock();
			return 0;
		}
		totalBytesRcvd += bytesRcvd; // Keep tally of total bytes
		buf[bytesRcvd] = '\0'; // Add \0 so printf knows where to stop
		printf("%s", buf); // Print the echo buffer
	}

	*/
	// Closing connection
	closesocket(socketServer);
	closesocket(socketClient);
	ClearWinSock();
	printf("\n");
	system("pause");
	return (0);
}