#ifndef ERRORS_HPP
#define ERRORS_HPP

#pragma once

#ifdef _WIN32
	#include <WinSock2.h>
#else
	#include <cerrno>
	#define SOCKET int
	#define INVALID_SOCKET ((int)-1)
	#define SOCKET_ERROR (int(-1))
#endif

namespace Sockets
{
	int GetError();
	enum class Errors {
#ifdef _WIN32
		WOULDBLOCK = WSAEWOULDBLOCK
#else
		WOULDBLOCK = EWOULDBLOCK
#endif
	};
}

#endif //ERRORS_HPP