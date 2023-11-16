import socket
from utils.bridge_utils.bridge_init import parse_bridge_file


def connect_to_bridge(ip_address, port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((ip_address, port))
            response = s.recv(1024).decode()
            return response, s
    except socket.error as e:
        print(f"Error connecting to {ip_address}:{port}: {e}")
        return "reject"


def connect_to_all_lans(interfaces):
    for interface in interfaces:
        port = None
        interface_dict = interface.to_dict()
        # print(interface_dict)

        bridges = parse_bridge_file()

        for bridge in bridges:

            if bridge.name == interface_dict['Lan Name']:
                print(bridge.name)
                print(interface_dict['Lan Name'])
                port = bridge.port

            if port:
                # Connect to the bridge
                response,s = connect_to_bridge(bridge.ip_address,port)

                if response == "accept":
                    print(f"Connected to {interface} bridge at {interface_dict['IP Address']}:{port}")

                    # function with loop
                else:
                    print(f"Connection to {interface} bridge at {interface_dict['IP Address']}:{port} rejected")


