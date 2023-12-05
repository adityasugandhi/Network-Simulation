# Authors as22cq (Aditya Sugandhi) & apf19e (Andrew Franklin)
import threading
import socket
import select
import sys
import time
import json

BRIDGE_FILE_PATH = 'utils/station_utils/bridge.txt'


class Bridge:
    def __init__(self, name, ip_address, port):
        self.name = name
        self.ip_address = ip_address
        self.port = port
        self.port_mapping = {}
        self.bridge_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.last_seen_times = {}
        self.active_ports = []
        self.exit_signal = threading.Event()
        self.lock = threading.Lock()
        self.check_connection_status_running = False

    def __str__(self) -> str:
        return f"{self.name},{self.ip_address},{self.port}"

    
    def update_mapping(self, socket_address, in_port):
        if socket_address not in self.port_mapping:
            self.port_mapping[socket_address] = {
                'in_port': in_port,
                'last_seen': time.time(),
                'mac_address': None
            }

    def update_macaddress(self,client_socket,macaddress):
        self.port_mapping[client_socket]['mac_address'] = macaddress

    def checkmacaddress(self,client_socket,macaddress):
        if macaddress in self.port_mapping.values():
            return True
        else:
            self.port_mapping[client_socket]['mac_address'] = macaddress
            print('new macaddress added to the self-learning table {},{}'.format(macaddress,self.port_mapping))
            return False

    def getportmap(self):
        return self.port_mapping

    def getsockaddr(self, target_mac):
        for source_address, info in self.port_mapping.items():
            # print(info)
            # print(source_address)
            if info['mac_address'] == target_mac:
                print('True')
                return source_address
        return None

    def fwdclient(self,socket_address,data):
        data = json.dumps(data)
        data = data.encode('utf-8')
        print(socket_address)
        socket_address.send(data)
        print('data succesfully sent to {}'.format(self.port_mapping[socket_address]))

    def shutdown_threads(self):
        self.exit_signal.set()

    def send_to_all(self, data, received_from_socket):
        data = json.dumps(data)
        print("sending to everyone")
        
        for client_socket, info in self.port_mapping.items():
            # if str(client_socket) != str(received_from_socket):
            if client_socket != received_from_socket:
                # print(info)
                # print('in')
                # print({client_socket}, {received_from_socket})
                # Skip sending data to the socket from which it was received
                try:
                    # client_socket.settimeout(1)
                    client_socket.send(data.encode('utf-8'))
                    # print(f"Sent data to {client_socket}")
                    # Add your acknowledgment and update_mapping logic here if needed
                except Exception as e:
                    print('Error sending/receiving data to/from {}: {}'.format(client_socket=client_socket, e=str(e)))


    def handle_station_data(self,client_socket,data):
        # print(len(self.port_mapping.keys()))
        client_port = self.port_mapping[client_socket]
        # print('here')
        if client_socket in self.port_mapping:
            # print(client_socket)
            # client_socket.send(b'data_received')
            # print('data-send')
            
            if data is not None:
                received_data = data
                
                # Extract or map variables
                in_port = client_socket.getpeername()[1]
                #source_name = received_data['Source Host']
                source_ip = received_data.get('Source IP', None)
                source_mac = received_data.get('Source MAC', None)
                dest_host = received_data.get('Dest Host', None)
                dest_ip = received_data.get('Dest IP', None)
                dest_mac = received_data.get('Dest MAC', None)
                type = received_data.get('Type', None)
                message = received_data.get('Message', None)
                flag = received_data.get('Acknowledgement', None)
                # print(source_mac,dest_mac)
                # source_mac is None and
                # if dest_mac is None:
                #     self.send_to_all(data, received_from_socket=client_socket) 
                
                # if type == 'ARP Reply Packet':
                #     if dest_mac is None:
                #         self.send_to_all(data, received_from_socket=client_socket)
                #     else:
                #         if self.checkmacaddress(client_socket,dest_mac):
                #             print(f'station found sending data to the client{dest_mac}{self.getsockaddr(dest_mac)}')
                #             forwading_socket = self.getsockaddr(dest_mac)
                #             self.fwdclient(forwading_socket,data)
                #         else:
                #             self.send_to_all(data, received_from_socket=client_socket)
                    
                
                # print(self.checkmacaddress(client_socket,source_mac))
                print('----------update mapping---------------------------')
                self.update_mapping(client_socket,in_port)
                # updates the macddress in learning table
                
                if source_mac == None:
                    self.update_macaddress(client_socket,source_mac)
                    # print(self.port_mapping)
                else:
                    print('source_mac is not none')
                print('-------------------------------------')
                print('source mac - {}  destination-mac {}, self.port_mapping'.format(source_mac,dest_mac))
                print('-------------------------------------')
                
                # if the dest_mac is in self-learning table then we fwd to the client
                if self.getsockaddr(dest_mac):
                    print('station found sending data to the client{}'.format(dest_mac)
                    forward_sock = self.getsockaddr(dest_mac)
                    self.fwdclient(forward_sock,data)
                else: 
                    print('station not found sending data to all the connections')
                    self.send_to_all(data,received_from_socket=client_socket)
                # self.send_to_all(data,received_from_socket=client_socket)

                if not data:
                    # Connection closed by the client
                    print("Connection closed by {}.".format(client_socket.getpeername()[1]))
    
    def show_port_mapping(self):
        if not self.port_mapping:
            print('self learning table is empty')
        # Iterate over the entries in self.port_mapping
        for socket_address,mapping_info in self.port_mapping.items():
            in_port = mapping_info['in_port']
            last_seen = mapping_info['last_seen']
            mac_address = mapping_info['mac_address']

            # Format the output as desired (assuming socket_address is an IP address)
            table = "| %-6s | %-20s | %s |" % (in_port, mac_address if mac_address is not None else 'N/A', time.ctime(last_seen))


# Print the table header
            print("+--------+----------------------+--------------------------+")
            print("| Port   | MAC Address          | Last Seen                |")
            print(table)
                
    def promptdisplay(self):
        sys.stdout.write('''
            show sl // show the contents of self-learning table
	    quit    // close the bridge
''')    
        sys.stdout.write(">> ")
        sys.stdout.flush() 

                    

                        
                        
       

    def check_connection_status(self):
        print("check_connection_status,started!!!")
        self.check_connection_status_running = True
        while not self.exit_signal.is_set():
            if len(self.port_mapping) != 0:
                with self.lock:
                    for source_address, info in list(self.port_mapping.items()):
                        if time.time() - info['last_seen'] > 60:
                            # Remove the mapping if no data has been received for 60 seconds
                            print("Station {} has timed out".format(source_address))
                            del self.port_mapping[source_address]
                time.sleep(30)
                self.check_connection_status_running = False
            else:
                time.sleep(10)
                continue
    def cheeek(self):
        print(self.port_mapping)
        
#
#This code defines a `Bridge` class that manages connections between different stations. It includes methods for updating the port mapping, handling station data, checking connection status, and sending data to all connected stations. The code also includes proper commenting to explain the purpose of each method and its functionality.