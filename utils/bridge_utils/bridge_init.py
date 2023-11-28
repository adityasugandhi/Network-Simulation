# Authors as22cq (Aditya Sugandhi) & apf19e (Andrew Franklin)
import threading
import socket
import select
import asyncio
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
            if info['mac_address'] == target_mac:
                return source_address
        return None

    def fwdclient(self,socket_address,data):
        socket_address.send(data)
        print(f'data succesfully sent to {self.port_mapping[socket_address]}')

    def shutdown_threads(self):
        self.exit_signal.set()

    def send_to_all(self, data):
        print("sending to everyone", data)
        for client_socket, info in self.port_mapping.items():
            try:
                client_socket.settimeout(1)
                client_socket.send(data.encode('utf-8'))
                acknowledgment = client_socket.recv(1024).decode('utf-8')

                if acknowledgment == 'Acknowledge':
                    print(f'Acknowledge received from {info["source_address"]}')
                    self.update_mapping(info["source_address"], info["in_port"])
                else:
                    print(f'Acknowledge not received from {info["source_address"]}')
            except Exception as e:
                print(f'Error sending/receiving data to/from {info["source_address"]}: {e}')

    def handle_station_data(self,client_socket,data):
        client_port = self.port_mapping[client_socket]

        if client_socket in self.port_mapping:
            print(client_socket)
            client_socket.send(b'data_received')
            print('data-send')
            
            if data is not None:
                received_data = json.loads(data.decode('utf-8'))
                print(received_data)
                # Extract or map variables
                in_port = client_socket.getpeername()[1]
                source_name = received_data['Source Name']
                source_ip = received_data['Source IP']
                source_mac = received_data['Source MAC']
                dest_host = received_data['Dest Host']
                dest_ip = received_data['Dest IP']
                dest_mac = received_data['Dest MAC']
                message = received_data['Message']
                flag = received_data['acknowledgement']
                print(data)
                print(source_mac,dest_mac)
                if source_mac is None and dest_mac is None:
                    self.send_to_all(data)
                    
                self.update_mapping(client_socket,in_port)
                self.update_macaddress(client_socket,source_mac)
                if self.getsockaddr(dest_mac):
                    self.fwdclient(client_socket,data)
                else: 
                    print('station not found sending data to all the connections')
                    self.send_to_all(data)

                if not data:
                    # Connection closed by the client
                    print(f"Connection closed by {client_socket.getpeername()[1]}")
                    
                    

                        
                        
       

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
#
#This code defines a `Bridge` class that manages connections between different stations. It includes methods for updating the port mapping, handling station data, checking connection status, and sending data to all connected stations. The code also includes proper commenting to explain the purpose of each method and its functionality.