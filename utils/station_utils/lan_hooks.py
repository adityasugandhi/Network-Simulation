# Authors as22cq (Aditya Sugandhi) & apf19e (Andrew Franklin)
import socket
#from utils.bridge_utils.bridge_init import parse_bridge_file
from utils.bridge_utils.bridge_parser import Bridgeparser
from utils.station_utils.station_parser import Interfaces,Interfaceparser
import threading
from utils.station_utils.arp_handling import ARPEntry, show_arp_table
import time
import json
import select
import sys
import pandas as pd

B = Bridgeparser()
ifaceparser = Interfaceparser()

class Lanhooks:
    def __init__(self) -> None:
        self.bridges = []
        self.arp_tables = {}
    
    def send_user_input_to_bridge(self, socket):
        while True:
            user_input = input("Enter your message and host to send message to in format host: message (type 'exit' to quit): ")
            host = user_input.split(':')[0]

            data_to_send = {
                'Source Name': 'Station',
                'Source IP': None,
                'Source MAC': None,
                'Dest Host': host,
                'Dest IP': None,
                'Dest MAC': None,
                'Message': user_input[len(host):],
                'Acknowledge': False
            }

            # for entry in self.arp_tables:
            #     self.arp_tables[entry].remove_stale_entries()

            if host.lower() in self.arp_tables:
                data_to_send['Dest IP'] = self.arp_tables[host.lower()].ip_address
                data_to_send['Dest MAC'] = self.arp_tables[host.lower()].mac_address

            json_data = json.dumps(data_to_send)
                

            if user_input.lower() == "exit":
                break

            try:
                socket.send(json_data.encode("utf-8"))
                print("Message sent.")

            except socket.error as e:
                print(f"Error sending data: {e}")
                break
        socket.close()


    def connect_to_bridge(self,ip_address, port, interface):
        try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
                print('------Connecting to server----')
                s.connect((ip_address, port))
                print('-----Waiting for response-----')
                response = s.recv(1024).decode()
                
                if response == 'accept':
                    print('-----Connection accepted-----')
                    #s.send(macaddress.encode())
                    print('-----Sending MAC address-----')
                    # print(type(s))

                    # Add ARP entry to the ARP table for the LAN
                    if interface['IP Address'] not in self.arp_tables:
                        self.arp_tables[interface['IP Address']] = ARPEntry(interface['Lan Name'], interface['Mac Address'], time.time())
   
                return response, s

        except socket.error as e:
            print(f"Error connecting to {ip_address}:{port}: {e}")
            return "reject"

    def connect_to_all_lans(self, interface_file):
        interfaces = ifaceparser.parse_interface_file(interface_file)
        connections = []
        for interface in interfaces:
            interface_dict = ifaceparser.interface_to_dict(interface)
   
            bridges = B.parse_bridge_file()

            for bridge in bridges:

                port = None
                if bridge.name == interface_dict['Lan Name']:
                    port = bridge.port
                    # print(port)
                else:
                    print(f"Bridge {interface_dict['Lan Name']} not found")

    
                if port:
                    # Connect to the bridge
                    response,s = self.connect_to_bridge(bridge.ip_address,port, interface_dict)

                    if response == "accept":
                        print(f"Connected to {bridge.name} bridge at {bridge.ip_address}:{bridge.port}")
                        connections.append({'Socket': s, 'Bridge': bridge, 'Interface': interface_dict })
                        
                    else:
                        print(f"Connection to {interface} bridge at {interface_dict['IP Address']}:{port} rejected")
        
        self.handle_arp(connections, interfaces)
 

    def handle_arp(self,connections,interfaces, is_router=False):
        sockets_list = [connection['Socket'] for connection in connections]
        
        should_listen = True
        prompt_displayed = False

        while should_listen:
            # Use select to wait for events on the sockets
            readable, _, _ = select.select(sockets_list + [sys.stdin], [], [], .1)

            # Print the default message prompt
            if not prompt_displayed:
                sys.stdout.write('''
            Station Supported Commands -
            send <destination> <message> // send message to a destination host
            show arp 		// show the ARP cache table information
            show pq 		// show the pending_queue
            show host 		// show the IP/name mapping table
            show iface 		// show the interface information
            show rtable 		// show the contents of routing table
            quit // close the station
                ''')
                sys.stdout.write(">> ")
                sys.stdout.flush()  # Flush to ensure the message is immediately displayed
                prompt_displayed = True

            for sock in readable:
                user_input = ''
                if sock == sys.stdin:
                    user_input = sys.stdin.readline().strip()
                    prompt_displayed = False

                    if user_input == 'show arp':
                        show_arp_table(self.arp_tables)
                    elif user_input == 'show pq':
                        pass
                    elif user_input == 'show host':
                        pass
                    elif user_input == 'show iface':
                        ifaceparser.show_ifaces(interfaces)
                    elif user_input == 'show rtable':
                        pass
                    elif user_input == 'quit':
                        for s in sockets_list:
                            s.close()
                        
                        should_listen = False
                    elif user_input[:4] == 'send' and not is_router and len(user_input.split(' ')) >= 3:
                        dest = user_input.split(' ')[1]
                        message = user_input[6 + len(dest):]
                        print(message)

                

    
    
    




