#include "Message.hpp"

unsigned char* Message::int2uChar(int i, int size) {
    if (size == 2) {
        unsigned char retour[2];
        retour[0] = i % 255;
        retour[1] = i / 255;
        return retour;
    }
    else if (size == 3) {
        unsigned char retour[3];
        retour[0] = i % 255;
        retour[1] = i / 255;
        retour[2] = i / (255 * 255);

        return retour;
    }
    else {
        unsigned char retour[] = { 0 };
        return retour;
    }
}

int Message::uChar2int(unsigned char* c, int size) {
    if (size == 2) {
        return (((int)c[1]) << 8) + ((int)c[0]);
    }
    else if (size == 3) {
        return (((int)c[2]) << 16) + (((int)c[1]) << 8) + ((int)c[0]);;
    }
    else {
        int retour = 0;
        return retour;
    }
}

FormatMsg Message::formatMessage(char* msg, int idMessage, int idEmetteur, int len) {
    FormatMsg message;
    for (int i = 0; i < len; i++) {
        message.msg[i] = msg[i];
    }
    unsigned char* test = int2uChar(idMessage, 2);
    message.idMsg_1 = test[0];
    message.idMsg_2 = test[1];

    message.idEmetteur_1 = int2uChar(idEmetteur, 3)[0];
    message.idEmetteur_2 = int2uChar(idEmetteur, 3)[1];
    message.idEmetteur_3 = int2uChar(idEmetteur, 3)[2];
    unsigned char* test2 = int2uChar(len + 1 + 2 + 2 + 3, 2);
    message.len_1 = test2[0];
    message.len_2 = test2[1];
    return message;
}

ReadMsg Message::readMessage(FormatMsg msg) {
    ReadMsg message;
    unsigned char leng[] = { msg.len_1, msg.len_2 };
    message.len = uChar2int(leng, 2) - 1 - 2 - 2 - 3;
    for (int i = 0; i < maxSizeMsg; i++) {
        if (i < message.len) {
            message.msg[i] = msg.msg[i];
        }
        else {
            message.msg[i] = 0;
        }
    }
    unsigned char idmessage[] = { msg.idMsg_1, msg.idMsg_2 };
    message.idMsg = uChar2int(idmessage, 2);
    unsigned char idEmetteur[] = { msg.idEmetteur_1, msg.idEmetteur_2, msg.idEmetteur_3 };
    message.idEmetteur = uChar2int(idEmetteur, 3);

    return message;
}

Message::Message() {
    char msg[] = { 0 };
    FormatMsg message_format = formatMessage(msg, 0, 0, 1);
    ReadMsg message = readMessage(message_format);
}
Message::Message(ReadMsg message) {
    message = message;
    message_format= formatMessage(message.msg, message.idMsg, message.idEmetteur, message.len);
}
Message::Message(FormatMsg message) {
    message_format = message;
    this->message = readMessage(message_format);
}
Message::Message(char* msg, int idMessage, int idEmetteur, int len) {
    message_format = formatMessage(msg, idMessage, idEmetteur, len);
    message = readMessage(message_format);
}

FormatMsg Message::msg2Send(void) {
    return message_format;
}
ReadMsg Message::msg2Read(void) {
    return message;
}