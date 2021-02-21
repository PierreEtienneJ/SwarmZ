#ifndef MESSAGE_HPP
#define MESSAGE_HPP

#pragma once

#define maxSizeMsg 30

struct FormatMsg {
    unsigned char debutTrame = 255;
    unsigned char len_1=0;
    unsigned char len_2=0;
    unsigned char idMsg_1=0;
    unsigned char idMsg_2=0;
    unsigned char idEmetteur_1=0;
    unsigned char idEmetteur_2=0;
    unsigned char idEmetteur_3=0;
    char msg[maxSizeMsg];
};

struct ReadMsg {
    unsigned char debutTrame = 255;
    int len; //2 bytes
    int idMsg; //2 bytes
    int idEmetteur;//3 bytes
    char msg[maxSizeMsg];
};

class Message{
private:
    FormatMsg message_format;
    ReadMsg message;

    unsigned char* int2uChar(int i, int size);
    int uChar2int(unsigned char* c, int size);

protected:
    FormatMsg formatMessage(char* msg, int idMessage, int idEmetteur, int len);
    ReadMsg readMessage(FormatMsg msg);

public:
    Message();
    Message(ReadMsg message);
    Message(FormatMsg message);
    Message(char* msg, int idMessage, int idEmetteur, int len);

    FormatMsg msg2Send(void);
    ReadMsg msg2Read(void);
};


#endif