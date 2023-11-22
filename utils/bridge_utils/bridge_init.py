import ipaddress
import socket
BRIDGE_FILE_PATH = 'utils/station_utils/bridge.txt'



class Bridge:
    def __init__(self, name, ip_address, port):
        self.name = name
        self.ip_address = ip_address
        self.port = port
        self.port_mapping = {}
        self.macaddress = {}
        self.bridge_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.last_seen_times = {}
        self.active_ports = []
    def update_mapping(self, source_address, in_port):
        # Update the port mapping with the learned port for the source address
        self.port_mapping[source_address] = in_port
    def update_macaddress(self,macaddress,name):
        self.macaddress[macaddress] = name
    def getportmap(self):
     return self.port_mapping
    
    
    
    
    
    


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

def forward_frame(self, data_frame, in_port):
        # Check if the mapping for the incoming port is defined
        if in_port not in self.port_mapping:
            # If not defined, forward the frame to all ports
            self.forward_to_all_ports(data_frame, in_port)
            # Update the mapping with the learned port for the source address
            self.update_mapping(data_frame['source_address'].iloc[0], in_port)
        else:
            # If the mapping is defined, forward the frame to the specified port
            out_port = self.port_mapping[in_port]
            self.forward_to_port(data_frame, in_port, out_port)

def forward_to_all_ports(self, data_frame, in_port):
        # Forward the frame to all ports except the incoming port
        for port in self.get_all_ports():
            if port != in_port:
                self.forward_to_port(data_frame, in_port, port)
def forward_to_port(self, data_frame, in_port, out_port):
        # Simulate forwarding the frame to a specific port
        print(f"Forwarding frame from port {in_port} to port {out_port}:")
        print(data_frame)
        print("")


