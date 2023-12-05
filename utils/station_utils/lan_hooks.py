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


B = Bridgeparser()
ifaceparser = Interfaceparser()
H = HostParser()
R = Routingparser()

class Lanhooks:
    def __init__(self):
        self.bridges = []
        self.arp_tables = {}
        self.pending_queue = []
    
    def getdefault_ips(self):
        default_ips = []
        
        for ip in self.arp_tables:
            if self.arp_tables[ip].default == True:
                default_ips.append(ip)
        return default_ips

    def connect_to_bridge(self, ip_address, port, interface):
        try:
        
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print('------Connecting to server----')
            sys.stdout.flush()  # Flush the buffer to ensure immediate display
            s.connect((ip_address, port))
            attempts = 0
            while attempts < 5:
                print('Trying to connect, Tries {}'.format(attempts))
                sys.stdout.flush()  # Flush the buffer to ensure immediate display
                readable, _, _ = select.select([s], [], [], 1)  # Check for readability with 1s timeout

                if s in readable:
                    print('-----Waiting for response-----')
                    sys.stdout.flush()  # Flush the buffer to ensure immediate display
                    response = s.recv(1024).decode()

                    if response == 'accept':
                        print('-----Connection accepted-----')
                        sys.stdout.flush()  # Flush the buffer to ensure immediate display

                        print('-----Sending Metadata-----')
                        sys.stdout.flush()  # Flush the buffer to ensure immediate display
                        self.metadata(interface, s)

                        # Add ARP entry to the ARP table for the LAN
                        if interface['IP Address'] not in self.arp_tables:
                            self.arp_tables[interface['IP Address']] = ARPEntry(interface['Lan Name'], interface['Mac Address'], time.time(), True)

                        return response, s
                    

                time.sleep(2)
                attempts += 1
            s.close()
            return 'reject' , None

        except socket.error as e:
            print("Error connecting to {}:{}: {}".format(ip_address, port, e))
            return "reject", None
    
    def connect_to_all_lans(self,router, interface_file, host_file, rt_file):
        interfaces = ifaceparser.parse_interface_file(interface_file)
        hosts = H.parse_hostname_file(host_file)
        rt_table = R.parse_routing_table_file(rt_file)

        connections = []
        for interface in interfaces:
            interface_dict = ifaceparser.interface_to_dict(interface)
   
            bridges = B.parse_bridge_file()
            if not bridges:
                print("Bridge {} not found".format(interface_dict['Lan Name']))
                return None
            
            for bridge in bridges:
                port = None
                if bridge.name == interface_dict['Lan Name']:
                    port = bridge.port
                    
                    mac_address = interface_dict['Mac Address']
                    # print(port)
                else:
                    print("Bridge {} not found".format(interface_dict['Lan Name']))

    
                if port:
                    # Connect to the bridge
                    response,s = self.connect_to_bridge(bridge.ip_address,port, interface_dict)

                    if response == "accept":
                        print("Connected to {} bridge at {}:{}".format(bridge.name, bridge.ip_address, bridge.port))
                        connections.append({'Socket': s, 'Bridge': bridge, 'Interface': interface_dict })

                        
                    else:   
                        print("Connection to {} bridge at {}:{} rejected".format(interface,interface_dict['Lan Name'],port))
                else:
                    print("Bridge {} not found".format(interface_dict['Lan Name']))
                    

        self.handle_arp(connections, router, interfaces, hosts, rt_table)
 
    def handle_bridge_disconnection(self, disconnected_socket, connections):
        disconnected_bridge = None
        for connection in connections:
            if connection['Socket'] == disconnected_socket:
                disconnected_bridge = connection['Bridge']
                break

        if disconnected_bridge:
            print("Bridge {} at {}:{} disconnected.".format(disconnected_bridge.name, disconnected_bridge.ip_address, disconnected_bridge.port))

            connections = [c for c in connections if c['Socket'] != disconnected_socket]
            #self.update_arp_table_on_disconnection(disconnected_bridge)

    def handle_arp(self,connections,router, interfaces,hosts, rt_table):
        try:
            sockets_list = [connection['Socket'] for connection in connections]
            
            should_listen = True
            prompt_displayed = False

            while should_listen:
                self.handle_arp_timeout()
                # Use select to wait for events on the sockets
                try:
                    readable, _, _ = select.select(sockets_list + [sys.stdin], [], [], .1)

                    # Print the default message prompt
                    if not prompt_displayed:
                        if router:
                            sys.stdout.write('''
                    Station Supported Commands -
                    show arp 		// show the ARP cache table information
                    show pq 		// show the pending_queue
                    show host 		// show the IP/name mapping table
                    show iface 		// show the interface information
                    show rtable 		// show the contents of routing table
                    quit // close the station
                                ''')
                        else:
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
                                print(show_arp_table(self.arp_tables,defaultips=self.getdefault_ips()))
                            elif user_input == 'show pq':
                                print(self.show_pending_queue())
                            elif user_input == 'show host':
                                print(H.show_hosts(hosts))
                            elif user_input == 'show iface':
                                print(ifaceparser.show_ifaces(interfaces))
                            elif user_input == 'show rtable':
                                print(R.show_routing_table(rt_table))
                            elif user_input == 'quit':
                                for s in sockets_list:
                                    s.close()
                                
                                should_listen = False
                            elif user_input[:4] == 'send' and not router and len(user_input.split(' ')) >= 3:
                                dest = user_input.split(' ')[1]
                                message = user_input[6 + len(dest):]
                                self.send_to_host(dest,message,hosts, rt_table, interfaces, sockets_list, connections)

                        else:
                            json_data = sock.recv(1024)
                            #print(f"Data received. from {sock.getpeername()}")
                            # sock.send('Acknowledge'.encode('utf-8'))
                            #data = json.loads(json_data)

                            if not json_data:
                                # Connection closed by bridge
                                print("Connection closed by {}".format(sock.getpeername()))
                                prompt_displayed =  False
                                self.handle_bridge_disconnection(sock, connections)
                                sockets_list = [s for s in sockets_list if s != sock]
                                sock.close()
                            else:
                                try: 
                                    data = json.loads(json_data)
                                
                                except json.decoder.JSONDecodeError as json_error:
                                    error_position = json_error.pos
                                    start_position = max(0, error_position - 10)  # Adjust the range as needed
                                    end_position = min(len(json_data), error_position + 10)  # Adjust the range as needed
                                    problematic_data = json_data[start_position:end_position]
                                    print("Problematic data: {}".format(problematic_data))
                                
                                    dest_ip = data.get('Dest IP', None)

                                if not router or dest_ip in self.getdefault_ips():
                                    
                                    # Process the received data
                                    # print(data)

                                    if data['Type'] == 'ARP Request Packet':
                        # If station has IP and MAC address mapping in own ARP table, send this info back to the station requesting MAC
                                        dest_ip = data['Dest IP']
                                        
                                        if dest_ip in self.arp_tables:
                                            # Access the ARP entry for the destination IP and retrieve the MAC address
                                            data['Dest MAC'] = self.arp_tables[dest_ip].mac_address
                                            # data['Type'] = 'ARP Reply Packet'

                                            reply_data = data
                                            orig_ip = data['Source IP']
                                            orig_mac = data['Source MAC']
                                            orig_host = data['Source Host']
                                            reply_data['Source IP'] = data['Dest IP']
                                            reply_data['Source MAC'] = data['Dest MAC']
                                            reply_data['Source Host'] = data['Dest Host']
                                            reply_data['Dest MAC'] = orig_mac
                                            reply_data['Dest IP'] = orig_ip
                                            reply_data['Dest Host'] = orig_host
                                            reply_data['Type'] = 'ARP Reply Packet'

                                            # print(reply_data)
                                            
                                            # Assuming 'sock' is a valid socket object
                                            sock.send(json.dumps(reply_data).encode('utf-8'))
                                            # self.send_to_host(reply_data['Dest IP'],None,hosts, rt_table, interfaces, sockets_list, connections)

                                        # If dont have source ip and mac mapping in station arp adds it
                                        if data['Source IP'] not in self.arp_tables:
                                            self.arp_tables[data['Source IP']] = ARPEntry(data['Source Host'], data['Source MAC'], time.time())
                                        else: # if already exists in arp table updates last seen time
                                            self.arp_tables[data['Source IP']].update_last_seen()

                                    elif data['Type'] == 'ARP Reply Packet':
                                        # print('here')
                                        # print(data)
                                        # If dont have dest ip and mac mapping in station arp adds it which it shouldn't because ideally would get this reply after sending request for it
                                        
                                        if data['Source IP'] not in self.arp_tables:
                                            self.arp_tables[data['Source IP']] = ARPEntry(data['Source Host'], data['Source MAC'], time.time())
                                        else: # if already exists in arp table updates last seen time
                                            self.arp_tables[data['Source IP']].update_last_seen()
                                        
                                        # Since we have arp reply should have packet in queue to be sent
                                        packet_to_send = self.check_valid_in_queue()
                                        print('----------')
                                        if packet_to_send:
                                            packet_to_send['Dest MAC'] = data['Source MAC']
                                            # self.send_to_host(packet_to_send['Dest IP'],packet_to_send['Message'],hosts, rt_table, interfaces, sockets_list, connections)
                                            self.send_message(packet_to_send, packet_to_send['Message'], sock)
                                            self.remove_from_queue(packet_to_send['Dest IP']) # Once queue message is sent remove from queue

                                    elif data['Type'] == 'IP Packet':
                                        print("Message received from host {}: {}".format(data['Source Host'], data['Message']))

                                        # If dont have source ip and mac mapping in station arp adds it
                                        if data['Source IP'] not in self.arp_tables:
                                            self.arp_tables[data['Source IP']] = ARPEntry(data['Source Host'], data['Source MAC'], time.time())
                                        else: # if already exists in arp table updates last seen time
                                            self.arp_tables[data['Source IP']].update_last_seen()

                                    else:
                                        print('Invalid Packet Received')
                                else:
                                    # if data['Type'] == 'ARP Reply Packet' or data['Type'] == 'ARP Request Packet':
                                        # print('here')
                                        # print(data)
                                        # If dont have dest ip and mac mapping in station arp adds it which it shouldn't because ideally would get this reply after sending request for it
                                        # if data['Source IP'] not in self.arp_tables:
                                        #     self.arp_tables[data['Source IP']] = ARPEntry(data['Source Host'], data['Source MAC'], time.time())
                                        # else: # if already exists in arp table updates last seen time
                                        #     self.arp_tables[data['Source IP']].update_last_seen()
                                        
                                        message = data.get('Message', None)
                                        source_host  = data.get('Source Host', None)
                                        self.send_to_host(data['Dest Host'],message,hosts, rt_table, interfaces, sockets_list, connections,router=True, data = data)
                                        if data['Source IP'] not in self.arp_tables:
                                            self.arp_tables[data['Source IP']] = ARPEntry(data['Source Host'], data['Source MAC'], time.time())
                                        else: # if already exists in arp table updates last seen time
                                            self.arp_tables[data['Source IP']].update_last_seen()

                                prompt_displayed = False

                except ConnectionResetError:
                        print("Station intentionally disconnected: {}".format(sock.getpeername()))
                        for connection in connections:
                            if sock == connection['Socket']:
                                del self.arp_tables[connection['Interface']['IP Address']]
                               # connections.remove(connection)
                                sock.close()
                                connections = [c for c in connections if c['Socket'] != sock]
                                sockets_list = [s for s in sockets_list if s != sock]
                                             
        except KeyboardInterrupt:
            print("\nKeyboardInterrupt received. Cleaning up and exiting...")
            self.cleanup_on_exit(connections)
            sys.exit()


    def send_to_host(self, dest, message, hosts, rt_table, interfaces, sockets_list, connections, router = False,data= None):

        if self.check_same_station(interfaces, dest):
            print('\nMessage received from interface on same station: {}'.format(message))
        else:
            dest_ip = H.get_host_ip(hosts, dest)
            dest_mac = None
            next_hop_interface = R.get_next_hop_interface(dest_ip, rt_table)
            # print(next_hop_interface)
            source_ip, source_mac, bridge_name = ifaceparser.bridge_forwarding_info(interfaces, next_hop_interface)
            if router:
                source_host = data.get('Source Host', None)
                source_mac = data.get('Source MAC', None)
                source_ip = data.get('Source IP', None)
                packet_type = data.get('Type', None) 
            else:
                packet_type = None
            # print(connections)
            # print(bridge_name)
            data_to_send = {
                'Source IP': source_ip,
                'Source MAC': source_mac,
                'Source Host': H.get_host_from_ip(hosts,source_ip),
                'Dest Host': dest,
                'Dest IP': dest_ip,
                'Dest MAC': dest_mac,
                'Type': packet_type,
            }
            
            idx_socket = self.get_socket_index(connections, bridge_name)

            # print(idx_socket)

            if idx_socket is not None:
                print('dest ip {}'.format(dest_ip))
                    
                if dest_ip in self.arp_tables:
                    dest_mac = self.arp_tables[dest_ip].mac_address
                    data_to_send['Dest MAC'] = dest_mac
                    self.send_message(data_to_send, message, sockets_list[idx_socket],router=router)
                else:
                    if router is not True:
                        self.arp_request(data_to_send,message, sockets_list[idx_socket])
                    # update arp table for router
                    
                    else:
                        
                        self.send_message(data_to_send, message, sockets_list[idx_socket], router=True)
                        
                        
            else:
                print('Trying to send on connection that does not exist')



    def send_message(self, data_to_send,msg=None, socket=None, router = False):
        if not router :
            data_to_send['Type'] = 'IP Packet'
        data_to_send['Message'] = msg

        json_data = json.dumps(data_to_send)


        try:
            
            socket.send(json_data.encode('utf-8'))
            print("Message sent.")

        except socket.error as e:
            print("Error sending data: {}".format(e))

    
    def arp_request(self, data_to_send, msg, socket):
        data_to_send['Type'] = 'ARP Request Packet'
        
        json_data = json.dumps(data_to_send)


        try:
            socket.send(json_data.encode('utf-8'))
            print("ARP Request sent.")
            data_to_send['Message'] = msg
            self.pending_queue.append(data_to_send)

        except socket.error as e:
            print("Error sending data: {}".format(e))
    

    def get_socket_index(self, connections, bridge_name):
        i = 0
        for c in connections:
            # print(c)
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
            'Type': 'metadata',
            'Message': None,
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
        

    def check_same_station(self, ifaces, iface_name):
        for iface in ifaces:
            if iface.name == iface_name:
                return True
        return False
    

    def handle_arp_timeout(self):
        keys_to_remove = []
        for ip in self.arp_tables:
            if  time.time() - self.arp_tables[ip].last_seen > 60 and not self.arp_tables[ip].default:
                keys_to_remove.append(ip)

        for ip in keys_to_remove:
            self.arp_tables.pop(ip)

    
    def cleanup_on_exit(self, connections):
        # Close all open sockets
        for connection in connections:
            connection['Socket'].close()







                

    
    
    




