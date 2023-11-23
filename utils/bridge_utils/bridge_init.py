import threading
import socket
import select
import time
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
    def update_mapping(self, source_address, in_port):
        self.port_mapping[source_address] = {
            'in_port': in_port,
            'last_seen': time.time(),
            'mac_address': None
        }
    def update_macaddress(self,client_socket,macaddress):
        self.port_mapping[client_socket]['mac_address'] = macaddress
    def getportmap(self):
     return self.port_mapping
    
    # gets socket address from port_mapping hash map.
    def getsockaddr(self, target_mac):
        for source_address, info in self.port_mapping.items():
            if info['mac_address'] == target_mac:
                return source_address
        return None

    def shutdown_threads(self):
        self.exit_signal.set()
    def send_to_all(self,data):
       for client_socket in self.port_mapping.items():
            client_socket.send(data)
            if client_socket.recv(1024).decode() == 'Acknowledge':
                print('Acknowledge received')
                _,client_port =client_socket.getpeername()
                self.update_mapping(client_socket,client_port)
            else:
                print(f'Acknowledge not received,{_}{client_port}')


    
    def handle_station_data(self,client_socket):
        client_port = self.port_mapping[client_socket]
    
        if client_socket in self.port_mapping:

            while not self.exit_signal.is_set():
                try:
                    # Check if there is data available to be read
                    readable, _, _ = select.select([client_socket], [], [], 1.0)  # 1.0 second timeout
                    if client_socket in readable:
                        data = client_socket.recv(1024)
                        # data[0] = macaddress
                        # data[1] = port number
                        self.update_mapping(client_socket,client_socket.getpeername()[1])
                        
                        if not data:
                            # Connection closed by the client
                            print(f"Connection closed by {client_socket.getpeername()[1]}")
                            break
                        else:
                            # Process the received data
                            
                            print(f"Received data from {client_socket.getpeername()}: {data.decode()}")
                            #Assumming first header file of the data is destination macaddress or ip.
                            if data[0] not in {info['mac_address'] for info in self.port_mapping.values()}:
                                self.send_to_all(data)

                            else:
                                senders_socket = self.getsockaddr(data[0])
                                print('MAC address already exists',senders_socket)
                                print('Sending Acknowledge')
                                client_socket.send('Acknowledge'.encode())

                            
                                
                except BlockingIOError:
                    # Handle the case where there is no data to read
                    pass
                except Exception as e:
                    print(f"Error receiving data: {e}")
                    
                    # Handle other exceptions if necessary
                    break
    def check_connection_status(self):
        print("check_connection_status,started!!!")
        while not self.exit_signal.is_set():
            if len(self.port_mapping ) !=0:
                for source_address, info in self.port_mapping.items():
                    if time.time() - info['last_seen'] > 60:
                        # Remove the mapping if no data has been received for 60 seconds
                        print(f"Station {source_address} has timed out")
                        del self.port_mapping[source_address]
                time.sleep(30)
            else:
                time.sleep(10)
                continue
    
        
        
    
    
    


# def parse_bridge_file():
#     bridges = []
#     with open(BRIDGE_FILE_PATH, 'r') as file:
#         for line in file:
#             # Split each line into tokens
#             tokens = line.strip().split(',')

#             # Check if the line has at least two tokens (name and IP address)
#             if len(tokens) >= 3:
#                 name = tokens[0]
#                 ip_address = tokens[1]
#                 port = int(tokens[2])
#                 bridges.append(Bridge(name,ip_address,port))
#     return bridges


# def remove_line_from_file(lan_name):

#     try:
#         # Read the file into a list
#         with open(BRIDGE_FILE_PATH, 'r') as file:
#             lines = file.readlines()

#         # Filter lines that do not match the specified values
#         updated_lines = [line for line in lines if lan_name not in line]

#         # Write the updated lines back to the file
#         with open(BRIDGE_FILE_PATH, 'w') as file:
#             file.writelines(updated_lines)
#     except:
#         print('File does not exist')


# def process_data_frame(data):
#     source_mac = data[:6]
#     dest_mac = data[6:12]
#     frame = data[12:]
#     return source_mac, dest_mac, frame

# def file_write(ip_addrr,PORT, station_name):
#     with open(BRIDGE_FILE_PATH, "a") as f:
#         f.write(f"{station_name},{ip_addrr},{PORT}\n")

# def forward_frame(self, data_frame, in_port):
#         # Check if the mapping for the incoming port is defined
#         if in_port not in self.port_mapping:
#             # If not defined, forward the frame to all ports
#             self.forward_to_all_ports(data_frame, in_port)
#             # Update the mapping with the learned port for the source address
#             self.update_mapping(data_frame['source_address'].iloc[0], in_port)
#         else:
#             # If the mapping is defined, forward the frame to the specified port
#             out_port = self.port_mapping[in_port]
#             self.forward_to_port(data_frame, in_port, out_port)

# def forward_to_all_ports(self, data_frame, in_port):
#         # Forward the frame to all ports except the incoming port
#         for port in self.get_all_ports():
#             if port != in_port:
#                 self.forward_to_port(data_frame, in_port, port)
# def forward_to_port(self, data_frame, in_port, out_port):
#         # Simulate forwarding the frame to a specific port
#         print(f"Forwarding frame from port {in_port} to port {out_port}:")
#         print(data_frame)
#         print("")


