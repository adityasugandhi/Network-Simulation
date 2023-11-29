# Authors as22cq (Aditya Sugandhi) & apf19e (Andrew Franklin)
import socket
#from utils.bridge_utils.bridge_init import parse_bridge_file
from utils.bridge_utils.bridge_parser import Bridgeparser
from utils.station_utils.station_parser import Interfaces,Interfaceparser, HostParser, Routingparser
import threading
from utils.station_utils.arp_handling import ARPEntry, show_arp_table
import time
import json
import select
import sys
import pandas as pd

B = Bridgeparser()
ifaceparser = Interfaceparser()
H = HostParser()
R = Routingparser()

class Lanhooks:
    def __init__(self) -> None:
        self.bridges = []
        self.arp_tables = {}
        self.pending_queue = []
    
   
    def connect_to_bridge(self,ip_address, port, interface):
        try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
                print('------Connecting to server----')
                s.connect((ip_address, port))
                print('-----Waiting for response-----')
                response = s.recv(1024).decode()
                
                if response == 'accept':
                    print('-----Connection accepted-----')
                    
                    print('-----Sending Metadata-----')
                    self.metadata(interface,s)

                    # Add ARP entry to the ARP table for the LAN
                    if interface['IP Address'] not in self.arp_tables:
                        self.arp_tables[interface['IP Address']] = ARPEntry(interface['Lan Name'], interface['Mac Address'], time.time())
   
                return response, s

        except socket.error as e:
            print(f"Error connecting to {ip_address}:{port}: {e}")
            return "reject"

    def connect_to_all_lans(self, interface_file, host_file, rt_file):
        interfaces = ifaceparser.parse_interface_file(interface_file)
        hosts = H.parse_hostname_file(host_file)
        rt_table = R.parse_routing_table_file(rt_file)

        connections = []
        for interface in interfaces:
            interface_dict = ifaceparser.interface_to_dict(interface)
   
            bridges = B.parse_bridge_file()

            for bridge in bridges:

                port = None
                if bridge.name == interface_dict['Lan Name']:
                    port = bridge.port
                    mac_address = interface_dict['Mac Address']
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
        
        self.handle_arp(connections, interfaces, hosts, rt_table)
 

    def handle_arp(self,connections,interfaces,hosts, rt_table, is_router=False):
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
                        self.show_pending_queue()
                    elif user_input == 'show host':
                        print(H.show_hosts(hosts))
                    elif user_input == 'show iface':
                        ifaceparser.show_ifaces(interfaces)
                    elif user_input == 'show rtable':
                        R.show_routing_table(rt_table)
                    elif user_input == 'quit':
                        for s in sockets_list:
                            s.close()
                        
                        should_listen = False
                    elif user_input[:4] == 'send' and not is_router and len(user_input.split(' ')) >= 3:
                        dest = user_input.split(' ')[1]
                        message = user_input[6 + len(dest):]
                        self.send_to_host(dest,message,hosts, rt_table, interfaces, sockets_list, connections)

                else:
                    json_data = sock.recv(1024)
                    data = json.loads(json_data)

                    if not data:
                        # Connection closed by bridge
                        print(f"Connection closed by {sock.getpeername()}")
                        sockets_list = [s for s in sockets_list if s != sock]
                        sock.close()
                    else:
                        # Process the received data
                        if data['Type'] == 'ARP Request Packet':
                            # If station has ip and mac address mapping in own arp table sends this info back to station requesting mac
                            if data['Dest IP'] in self.arp_tables:
                                data['Dest MAC'] = self.arp_tables['Dest IP'].mac_address
                                data['Type'] = 'ARP Reply Packet'
                                sock.send(json.dumps(data).encode('utf-8'))

                            # If dont have source ip and mac mapping in station arp adds it
                            if data['Source IP'] not in self.arp_tables:
                                self.arp_tables[data['Source IP']] = ARPEntry(data['Source Host'], data['Source MAC'], time.time())
                            else: # if already exists in arp table updates last seen time
                                self.arp_tables[data['Source IP']].update_last_seen()

                        elif data['Type'] == 'ARP Reply Packet':
                            # If dont have source ip and mac mapping in station arp adds it
                            if data['Dest IP'] not in self.arp_tables:
                                self.arp_tables['Source IP'] = ARPEntry(data['Source Host'], data['Source MAC'], time.time())
                            else: # if already exists in arp table updates last seen time
                                self.arp_tables[data['Source IP']].update_last_seen()
                            packet_to_send = self.check_valid_in_queue()
                        elif data['Type'] == 'IP Packet':
                            pass
                        else:
                            print('Invalid Packet Received')


    def send_to_host(self, dest, message, hosts, rt_table, interfaces, sockets_list, connections):
        dest_ip = H.get_host_ip(hosts, dest)
        dest_mac = None
        next_hop_interface = R.get_next_hop_interface(dest_ip, rt_table)
        source_ip, source_mac, bridge_name = ifaceparser.bridge_forwarding_info(interfaces, next_hop_interface)
        
        data_to_send = {
            'Source IP': source_ip,
            'Source MAC': source_mac,
            'Source Host': H.get_host_from_ip(hosts,source_ip),
            'Dest Host': dest,
            'Dest IP': dest_ip,
            'Dest MAC': dest_mac,
        }
        
        idx_socket = self.get_socket_index(connections, bridge_name)

        if dest_ip in self.arp_tables:
            dest_mac = self.arp_tables[dest_ip]
            self.send_message(data_to_send, message, sockets_list[idx_socket])
        else:
            self.arp_request(data_to_send,message, sockets_list[idx_socket])



    def send_message(self, data_to_send, msg, socket):
        data_to_send['Type'] = 'IP Packet'
        data_to_send['Message'] = msg

        json_data = json.dumps(data_to_send)


        try:
            socket.send(json_data.encode('utf-8'))
            print("Message sent.")

        except socket.error as e:
            print(f"Error sending data: {e}")

    
    def arp_request(self, data_to_send, msg, socket):
        data_to_send['Type'] = 'ARP Request Packet'
        
        json_data = json.dumps(data_to_send)


        try:
            socket.send(json_data.encode('utf-8'))
            print("ARP Request sent.")
            data_to_send['Message'] = msg
            self.pending_queue.append(data_to_send)

        except socket.error as e:
            print(f"Error sending data: {e}")
    

    def get_socket_index(self, connections, bridge_name):
        i = 0
        for c in connections:
            if c['Interface']['Lan Name'] == bridge_name:
                return i
            else:
                i += 1
    
    def metadata(self,interface,client_socket):
        data_to_send = {
            'Source IP': interface['IP Address'],
            'Source MAC': interface['Mac Address'],
            'Dest Host': None,
            'Dest IP': None,
            'Dest MAC': None,
            'Message': 'metadata',
            'Acknowledge': False
        }
        json_data = json.dumps(data_to_send)
        client_socket.send(json_data.encode('utf-8'))
        print('metadata sent')


    def check_valid_in_queue(self):
        for ip_packet in self.pending_queue:
            if ip_packet['Dest IP'] in self.arp_tables:
                return ip_packet
        return None
    
    def remove_from_queue(self,ip):
        self.pending_queue = [q for q in self.pending_queue if q['Dest IP'] != ip]

    def show_pending_queue(self):
        for ip in self.pending_queue:
            print(ip)
        





                

    
    
    




