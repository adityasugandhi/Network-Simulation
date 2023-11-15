import socket
from utils.settings import PORT


def connect_to_bridge(ip_address):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((ip_address, PORT))
            response = s.recv(1024).decode()
            return response
    except socket.error as e:
        print(f"Error connecting to {ip_address}:{PORT}: {e}")
        return "reject"


def connect_to_all_lans(interfaces):
    for interface in interfaces:
        interface_dict = interface.to_dict()
        
        # Connect to the bridge
        response = connect_to_bridge(interface_dict['IP Address'])

        if response == "accept":
            print(f"Connected to {interface} bridge at {interface_dict['IP Address']}:{PORT}")
        else:
            print(f"Connection to {interface} bridge at {interface_dict['IP Address']}:{PORT} rejected")