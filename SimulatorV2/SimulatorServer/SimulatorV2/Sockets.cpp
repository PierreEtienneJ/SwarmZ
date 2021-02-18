#include "Sockets.hpp"

namespace Sockets
{
	bool Start()
	{
#ifdef _WIN32
		WSAData wsaData;
		return WSAStartup(MAKEWORD(2, 2), &wsaData) == 0;
#else
		return true;
#endif
	}
	void Release()
	{
#ifdef _WIN32
		WSACleanup();
#endif
	}
	bool SetNonBlocking(SOCKET socket)
	{
#ifdef _WIN32
		u_long mode = 1;
		return ioctlsocket(socket, FIONBIO, &mode) == 0;
#else
		return fcntl(socket, F_SETFL, O_NONBLOCK) != -1;
#endif
	}
	void CloseSocket(SOCKET s)
	{
#ifdef _WIN32
		closesocket(s);
#else
		close(s);
#endif
	}
	std::string GetAddress(const sockaddr_in& addr)
	{
		char buff[INET6_ADDRSTRLEN] = { 0 };
		return inet_ntop(addr.sin_family, (void*)&(addr.sin_addr), buff, INET6_ADDRSTRLEN);
	}
}
