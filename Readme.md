# Network Simulation

Components:

* Bridges

```
  python bridge.py <bridge name> <no of ports>
```

* Bridge CMD Line interface :

  * show sl --> To display current ports and macaddress in the self.learning table
  * quit -> To shutdown
* Router

  * ```
    python station.py --route <interface> <routingtable> <hosts> 
    ```
* Stations
* ```
  python station.py --no <interface> <routingtable> <hosts> 
  ```
  Station  & Router Supported Commands -

  send `<destination>` `<message>` // send message to a destination host

  show arp        // show the ARP cache table information

  show pq         // show the pending_queue

  show host       // show the IP/name mapping table

  show iface      // show the interface information

  show rtable         // show the contents of routing table

  quit // close the station
