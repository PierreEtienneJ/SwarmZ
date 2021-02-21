#include "Sockets.hpp"
#include "Errors.hpp"
#include "Message.hpp"
#include "Server.hpp"

#include <iostream>
#include <string>
#include <vector>

int main(){
	Server serv(3000);
	serv.start(true);
	serv.run(true);
}
