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
	int GetError()
	{
#ifdef _WIN32
		return WSAGetLastError();
#else
		return errno;
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
}
