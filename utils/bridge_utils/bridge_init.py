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
        self.port_mapping[socket_address] = {
            'in_port': in_port,
            'last_seen': time.time(),
            'mac_address': None
        }

    def update_macaddress(self,client_socket,macaddress):
        self.port_mapping[client_socket]['mac_address'] = macaddress

    def getportmap(self):
        return self.port_mapping

    def getsockaddr(self, target_mac):
        for source_address, info in self.port_mapping.items():
            print(f' checking is targetmac is in port_mapping {info["mac_address"]}, {target_mac},{self.port_mapping}')
            if info['mac_address'] == target_mac:
                return source_address
        return None

    def fwdclient(self,socket_address,data):
        data = json.dumps(data)
        data = data.encode('utf-8')
        socket_address.send(data)
        print(f'data succesfully sent to {self.port_mapping[socket_address]}')

    def shutdown_threads(self):
        self.exit_signal.set()

    def send_to_all(self, data, received_from_socket):
        data = json.dumps(data)
        print("sending to everyone")
        
        for client_socket, info in self.port_mapping.items():
            if str(client_socket) != str(received_from_socket):
                print(f"{client_socket}, {received_from_socket}")
                # Skip sending data to the socket from which it was received
                try:
                    client_socket.settimeout(1)
                    client_socket.send(data.encode('utf-8'))
                    print(f"Sent data to {client_socket}")
                    # Add your acknowledgment and update_mapping logic here if needed
                except Exception as e:
                    print(f'Error sending/receiving data to/from {client_socket}: {e}')


    def handle_station_data(self,client_socket,data):
        client_port = self.port_mapping[client_socket]
        print('here')
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

                message = received_data.get('Message', None)
                flag = received_data.get('Acknowledgement', None)
                print(source_mac,dest_mac)
                if source_mac is None and dest_mac is None:
                    self.send_to_all(data, received_from_socket=client_socket) 
                
                self.update_mapping(client_socket,in_port)
                # updates the macddress in learning table
                self.update_macaddress(client_socket,source_mac)
                
                # if the dest_mac is in self-learning table then we fwd to the client
                if self.getsockaddr(dest_mac):
                    print(f'station found sending data to the client{dest_mac}{self.getsockaddr(dest_mac)}')
                    self.fwdclient(client_socket,data)
                else: 
                    print('station not found sending data to all the connections')
                    self.send_to_all(data,received_from_socket=client_socket)

                if not data:
                    # Connection closed by the client
                    print(f"Connection closed by {client_socket.getpeername()[1]}")
    
    def show_port_mapping(self):
        if not self.port_mapping:
            print('self learning table is empty')
        # Iterate over the entries in self.port_mapping
        for socket_address,mapping_info in self.port_mapping.items():
            in_port = mapping_info['in_port']
            last_seen = mapping_info['last_seen']
            mac_address = mapping_info['mac_address']

            # Format the output as desired (assuming socket_address is an IP address)
            table = f"| {in_port:<6} | {mac_address if mac_address is not None else 'N/A':<20} | {time.ctime(last_seen)} |"

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
                            print(f"Station {source_address} has timed out")
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