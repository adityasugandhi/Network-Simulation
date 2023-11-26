# Authors as22cq (Aditya Sugandhi) & apf19e (Andrew Franklin)
import socket
#from utils.bridge_utils.bridge_init import parse_bridge_file
from utils.bridge_utils.bridge_parser import Bridgeparser
from utils.station_utils.station_parser import Interfaces,Interfaceparser
import threading
from utils.station_utils.arp_handling import ARPTable
import time
import json

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
                'Message': user_input[len(host):]
            }

            # for entry in self.arp_tables:
            #     self.arp_tables[entry].remove_stale_entries()

            if host in self.arp_tables:
                data_to_send['Dest IP'] = self.arp_tables[host].ip_address
                data_to_send['Dest MAC'] = self.arp_tables[host].mac_address

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
                    print(type(s))

                    # Add ARP entry to the ARP table for the LAN
                    if interface['Lan Name'].lower() not in self.arp_tables:
                        self.arp_tables[interface['Lan Name'].lower()] = ARPTable()

                        # arp_table = self.arp_tables[interface_dict['Lan Name']]
                        # arp_table.add_arp_entry(interface_dict['IP Address'], interface_dict['Mac Address'])
                        self.arp_tables[interface['Lan Name'].lower()].add_arp_entry(interface['IP Address'], interface['Mac Address'])

                    # Start a thread for handling ARP requests
                    # threading.Thread(target=self.arp_handler, args=(interface['Lan Name'],)).start()
                    threading.Thread(target=self.send_user_input_to_bridge,args=(s,)).start()
                   
                return response, s

        except socket.error as e:
            print(f"Error connecting to {ip_address}:{port}: {e}")
            return "reject"

    def connect_to_all_lans(self, interface_file):
        interfaces = ifaceparser.parse_interface_file(interface_file)
        connections = []
        for interface in interfaces:
            interface_dict = ifaceparser.interface_to_dict(interface)
            # print(interface_dict)
            #print(interface_dict)

            bridges = B.parse_bridge_file()

        
            for bridge in bridges:
                # print(bridge.name)
                # print(interface_dict['Lan Name'])
                port = None
                if bridge.name == interface_dict['Lan Name']:
                    # print(bridge.name)
                    # print(interface_dict['Lan Name'])
                    port = bridge.port
                    print(port)
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

        return connections
    
    def send_to_bridge(self, connections, message):
        connections.send(message.encode())
    # BEGIN: be15d9bcejpp
    # END: be15d9bcejpp

    def arp_handler(self,lan_name):
        arp_table = self.arp_tables[lan_name]
        while True:
            # Simulate ARP handling (replace this with actual ARP handling logic)
            print(f"Handling ARP requests for LAN: {lan_name}")
            print("ARP Table:")
            for entry in arp_table.arp_entries:
                print(f"IP: {entry.ip_address}, MAC: {entry.mac_address}")
            # Sleep for a while before handling the next ARP request
            time.sleep(5)

    
    
    




