/*-------------------------------------------------------*/
#include <stdio.h>
#include <sys/types.h>
#include <sys/time.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netdb.h>
#include <arpa/inet.h>
#include <signal.h>
#include <sys/wait.h>
#include <errno.h>
#include <string.h>
#include <strings.h>
#include <stdlib.h>
/*----------------------------------------------------------------*/


/*----------------------------------------------------------------*/
/* station : gets hooked to all the lans in its ifaces file, sends/recvs pkts */
/* usage: station <-no -route> interface routingtable hostname */
main (int argc, char *argv[])
{

  /* initialization of hosts, interface, and routing tables */
    
  /* hook to the lans that the station should connected to
   * note that a station may need to be connected to multilple lans
   */
  
  /* monitoring input from users and bridges
   * 1. from user: analyze the user input and send to the destination if necessary
   * 2. from bridge: check if it is for the station. Note two types of data
   * in the ethernet frame: ARP packet and IP packet.
   *
   * for a router, it may need to forward the IP packet
   */
}



