#include "Errors.hpp"

namespace Sockets
{
	int GetError()
	{
#ifdef _WIN32
		return WSAGetLastError();
#else
		return errno;
#endif
	}
}