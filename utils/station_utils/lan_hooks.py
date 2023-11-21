import socket
#from utils.bridge_utils.bridge_init import parse_bridge_file
from utils.bridge_utils.bridge_parser import Bridgeparser
from utils.station_utils.station_parser import Interfaces,Interfaceparser
B = Bridgeparser()
ifaceparser = Interfaceparser()
class Lanhooks:
    def __init__(self) -> None:
        self.bridges = []
    @staticmethod
    def connect_to_bridge(ip_address, port, macaddress):
        try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
                print('------Connecting to server----')
                s.connect((ip_address, port))
                #s.send(macaddress.encode())
                print('-----Waiting for response-----')
                response = s.recv(1024).decode()
                if response == 'accept':
                    print('-----Connection accepted-----')
                    s.send(macaddress.encode())
                return response, s
        except socket.error as e:
            print(f"Error connecting to {ip_address}:{port}: {e}")
            return "reject"

    def connect_to_all_lans(self, interace_file):
        interfaces = ifaceparser.parse_interface_file(interace_file)
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
                    response,s = self.connect_to_bridge(bridge.ip_address,port, interface_dict['Mac Address'])

                    if response == "accept":
                        print(f"Connected to {bridge.name} bridge at {bridge.ip_address}:{bridge.port}")
                        connections.append({'Socket': s, 'Bridge': bridge, 'Interface': interface_dict })
                        
                        # function with loop
                    else:
                        print(f"Connection to {interface} bridge at {interface_dict['IP Address']}:{port} rejected")

        return connections


