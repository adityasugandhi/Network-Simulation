/*----------------------------------------------------------------*/
#include <stdio.h>
#include <sys/types.h>
#include <sys/time.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <malloc.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <signal.h>
#include <sys/wait.h>
#include <errno.h>
#include <string.h>
#include <netdb.h>
#include <arpa/inet.h>
/*----------------------------------------------------------------*/


/* bridge : recvs pkts and relays them */
/* usage: bridge lan-name max-port */
int 
main (int argc, char *argv[])
{
  /* create the symbolic links to its address and port number
   * so that others (stations/routers) can connect to it
   */
  
  /* listen to the socket.
   * two cases:
   * 1. connection open/close request from stations/routers
   * 2. regular data packets
   */
}
/*----------------------------------------------------------------*/
