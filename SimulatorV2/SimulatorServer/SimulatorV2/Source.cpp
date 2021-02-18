/*
 * Auteur: Butterfly/SupaFresh
 *
 * Code source d'un serveur qui attend la connexion d'un client,
 * qui lit et affiche les messages envoyés.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <arpa/inet.h>
#include <poll.h>
#include <errno.h>

#define bool int
#define false 0
#define true 1

int lire(char* str, int len);
void viderBuffer();

int main()
{
    int sock = socket(AF_INET, SOCK_STREAM, 0);

    if (sock == -1)
    {
        perror("socket");
        return errno;
    }

    struct sockaddr_in sin;

    sin.sin_family = AF_INET;
    sin.sin_port = htons(2000);
    sin.sin_addr.s_addr = htonl(INADDR_ANY); /* INADDR_ANY = localhost = 127.0.0.21 = le Pc utilise, htonl = Host To Network Long parceque l'adresse IP est sous 32 bits */

    /* Bind sert a lier la socket sur un port, elle prend les meme parametres que connect */
    if (bind(sock, (struct sockaddr*)&sin, sizeof(struct sockaddr)) < 0)
    {
        perror("bind");
        return errno;
    }

    /* Listen ecoute sur le port, cette fonction prend en parametre la socket et le nombre de client qu'il veut */
    if (listen(sock, 1) == -1)
    {
        perror("listen");
        return errno;
    }

    int csock; /* La socket du client */
    struct sockaddr_in csin; /* La structure du client */
    int sinsize = sizeof(csin);

    /* accept en parametre la socket serveur, la structure du client convertis en sockaddr qu'elle remplira, la taille de la structure du client, elle renvois la socket client */
    if ((csock = accept(sock, (struct sockaddr*)&csin, &sinsize)) < 0)
    {
        perror("accept");
        return errno;
    }

    char nom[20]; /* Nom du client */

    /* read lit sur la socket mise en parametre, elle prends en parametre la socket que l'on veut lire, la variable a remplir et la taille de cette variable */
    if (read(csock, &nom, sizeof(nom)) == -1)
    {
        perror("read nom");
        return errno;
    }

    printf("%s s'est connecte.\n", nom);

    char buffer[1024];

    bool continuer = true;
    do
    {
        if (read(csock, buffer, sizeof(buffer)) == -1)
        {
            perror("read");
            return errno;
        }

        if (strcmp(buffer, "007") == 0)
            continuer = false;
        else
            printf("%s: %s.\n", nom, buffer);
    } while (continuer == true);

    printf("%s s'est deconnecte.\n", nom);

    close(sock);

    return EXIT_SUCCESS;
}

void viderBuffer()
{
    int c = 0;
    while (c != '\n' && c != EOF)
    {
        c = getchar();
    }
}

int lire(char* str, int len)
{
    char* pos = NULL;

    if (fgets(str, len, stdin) != NULL)
    {
        pos = strchr(str, '\n');
        if (pos != NULL)
        {
            *pos = '\0';
        }
        else
        {
            viderBuffer();
        }
        return 1;
    }

    viderBuffer();
    return 0;

}
