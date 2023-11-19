import socket
#from utils.bridge_utils.bridge_init import parse_bridge_file
from utils.bridge_utils.bridge_parser import Bridgeparser

B = Bridgeparser()

def connect_to_bridge(ip_address, port, macaddress):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            print('------Connecting to server----')
            s.connect((ip_address, port))
            s.send(macaddress.encode())
            print('-----Waiting for response-----')
            response = s.recv(1024).decode()
            if response == 'accept':
                print('-----Connection accepted-----')
                s.send(macaddress.encode())
            return response, s
    except socket.error as e:
        print(f"Error connecting to {ip_address}:{port}: {e}")
        return "reject"


def connect_to_all_lans(interfaces):
    for interface in interfaces:
        port = None
        interface_dict = interface.to_dict()
        #print(interface_dict)

        bridges = B.parse_bridge_file()

        for bridge in bridges:

            if bridge.name == interface_dict['Lan Name']:
                print(bridge.name)
                print(interface_dict['Lan Name'])
                port = bridge.port
            else:
                print(f"Bridge {interface_dict['Lan Name']} not found")
            if port:
                # Connect to the bridge
                response,s = connect_to_bridge(bridge.ip_address,port, interface_dict['Mac Address'])

                if response == "accept":
                    print(f"Connected to {bridge.name} bridge at {bridge.ip_address}:{bridge.port}")
                    
                    # function with loop
                else:
                    print(f"Connection to {interface} bridge at {interface_dict['IP Address']}:{port} rejected")


