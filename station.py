
import socket
import system
hostfile_path  = "C:\Users\as22cq\Downloads\Project2\project\hosts.txt"
arp_cache = {}



#---------- Bridge class to store bridge ip_address, port & name---------
class Bridge:
    def __init__(self,name,ip_address, port):
        self.name = name
        self.ip_address = ip_address
        self.port = port
def bridge_read(filepath):
    bridge_parts = []
    with open(filepath,'r') as bf:
        lines = bf.readlines()
        print(lines)
        for line in lines:
            parts =  line.split(',')
            bridge_parts.append(parts)
            
        return bridge_parts


#---------- Host class to store host name & ip_address---------
class Interface:
    def __init__(self, name, ip_address, subnet_mask, mac_address, lan_name):
        self.name = name
        self.ip_address = ip_address
        self.subnet_mask = subnet_mask
        self.mac_address = mac_address
        self.lan_name = lan_name
def parse_interface_file(file_path):
    interfaces = []
    with open(file_path, 'r') as file:
        for line in file:
            # Split each line into tokens
            tokens = line.strip().split()

            # Check if the line has at least five tokens (name, IP, subnet mask, MAC, LAN)
            if len(tokens) >= 5:
                name = tokens[0]
                ip_address = tokens[1]
                subnet_mask = tokens[2]
                mac_address = tokens[3]
                lan_name = tokens[4]
                interface = Interface(name, ip_address, subnet_mask, mac_address, lan_name)
                interfaces.append(interface)
    
    return interfaces
# Initializing TCP Connections to all the bridges in bridge file.

def receive_frame(interface):
    # Assume 'receive_ethernet_frame' is a function to receive Ethernet frames
    ethernet_frame = receive_ethernet_frame(interface)

    # Parse the Ethernet frame to extract the IP packet
    ip_packet = extract_ip_packet(ethernet_frame)

    # Check if the IP packet is destined for this station
    if ip_packet.destination_ip == interface.ip_address:
        # Display the message and sender's name
        print(f"Received message from {ip_packet.source_name}: {ip_packet.message}")

def handle_arp_packet(arp_packet, arp_cache):
    if arp_packet['type'] == 'request':
        # Respond with this station's MAC address
        send_arp_reply(arp_packet['sender_ip'], this_station_mac)
    elif arp_packet['type'] == 'reply':
        # Update the ARP cache with the sender's information
        update_arp_cache(arp_cache, arp_packet['sender_ip'], arp_packet['sender_mac'])

def consult_forwarding_table(destination_ip):
    # TODO: Implement the logic to consult the forwarding table
    # Return the next hop IP address based on the destination IP
      # Assume a simple forwarding table mapping destination IPs to next hop IPs
    forwarding_table = {
        '128.252.11.0': '128.252.11.1',
        '128.252.13.32': '128.252.13.33',
        '0.0.0.0': '128.252.13.38'
        # Add more entries as needed
    }

    return forwarding_table.get(destination_ip, None)


def create_arp_packet(packet_type, sender_ip, target_ip, sender_mac):
    # Assuming a simple ARP packet structure
    arp_packet = {
        'type': packet_type,
        'sender_ip': sender_ip,
        'target_ip': target_ip,
        'sender_mac': sender_mac
        # Add more fields as needed
    }
    return arp_packet

def create_ip_packet(destination_ip, source_ip, message):
    # Simple IP packet structure with source and destination IPs and a message
    ip_packet = {
        'source_ip': source_ip,
        'destination_ip': destination_ip,
        'message': message
    }
    return ip_packet

def send_packet_to_mac_layer(next_hop_mac, ip_packet):
    # Assume a simple structure for the Ethernet frame
    ethernet_frame = {
        'source_mac': this_station_mac,
        'destination_mac': next_hop_mac,
        'payload': ip_packet
    }
    # TODO: Implement the logic to send the Ethernet frame
    # In a real-world scenario, this would involve sending the frame over the network using appropriate networking libraries or APIs
    print(f"Sending Ethernet frame to {next_hop_mac}: {ethernet_frame}")
    return ethernet_frame

def receive_ethernet_frame(interface):
    # TODO: Implement the logic to receive an Ethernet frame from the interface
    # In a real-world scenario, this would involve listening for incoming frames on the specified interface
    # For simulation purposes, you can use a placeholder value
    received_frame = {'source_mac': '00:00:00:00:00:01', 'destination_mac': '00:00:00:00:00:02', 'payload': 'Hello from Ethernet frame'}
    print(f"Received Ethernet frame: {received_frame}")
    return received_frame

def extract_ip_packet(ethernet_frame):
    # Simple extraction assuming the IP packet is directly in the payload
    return ethernet_frame['payload']

def send_arp_reply(requester_ip, this_station_mac):
    # Create an ARP reply packet
    arp_reply = create_arp_packet('reply', this_station_ip, requester_ip, this_station_mac)
    # TODO: Send the ARP reply packet
    # In a real-world scenario, this would involve sending the ARP reply over the network
    print(f"Sending ARP reply to {requester_ip}: {arp_reply}")
    return arp_reply

def update_arp_cache(arp_cache, ip_address, mac_address):
    # Update the ARP cache with the received information
    arp_cache[ip_address] = mac_address
    print(f"Updated ARP cache: {arp_cache}")

def send_message(hosts, destination_name, message):
    # Look up the destination IP address based on the destination name
    destination_ip = next((host.ip_address for host in hosts if host.name == destination_name), None)

    if destination_ip:
        # Consult the forwarding table to determine the next hop (assuming you have a forwarding table)
        next_hop_ip = consult_forwarding_table(destination_ip)

        # Perform ARP resolution to get the MAC address of the next hop
        next_hop_mac = arp_resolution(next_hop_ip)

        # Create an IP packet and pass it to the MAC layer for sending
        ip_packet = create_ip_packet(destination_ip, this_station_ip, message)
        send_packet_to_mac_layer(next_hop_mac, ip_packet)
    else:
        print(f"Destination {destination_name} not found in the host list.")
def handle_station_tasks(interface, hosts):
    # Example: Send a message
    send_message(hosts, 'Acs2', 'Hello from Acs1!')

    # Example: Receive a message
    receive_frame(interface)

    # Example: Handle ARP request
    handle_arp_packet('ARP REQUEST EXAMPLE')


def arp_resolution(ip_address): 
     if ip_address in arp_cache:
        return arp_cache[ip_address]

    # If not in the cache, send an ARP request to get the MAC address
    arp_request = create_arp_packet('request', this_station_ip, ip_address, this_station_mac)
    send_packet_to_mac_layer('broadcast', arp_request)

    # Wait for the ARP reply
    arp_reply = receive_ethernet_frame(interface)
    if arp_reply:
        # Update the ARP cache with the received information
        update_arp_cache(arp_cache, arp_reply['source_ip'], arp_reply['source_mac'])
        return arp_reply['source_mac']
    else:
        print(f"ARP resolution for {ip_address} failed.")
        return None
    # TODO: Implement the logic to perform ARP resolution
    # Return the MAC address corresponding to the given IP address
    


def parse_hostname_file(file_path):
    hosts = []
    with open(file_path, 'r') as file:
        for line in file:
            # Split each line into tokens
            tokens = line.strip().split()

            # Check if the line has at least two tokens (name and IP address)
            if len(tokens) >= 2:
                name = tokens[0]
                ip_address = tokens[1]
                host = Host(name, ip_address)
                hosts.append(host)
    return hosts
def connect_to_lans(interfaces, bridges):
    bridges = parse_bridge_file(bridge_file_path)
    for interface in interfaces:
        # Find the corresponding bridge information based on the LAN name
        bridge_info = next((b for b in bridges if b.name == interface.lan_name), None)

        if bridge_info:
            # Use TCP socket to connect to the bridge
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(5)  # Socket timeout 5 secs.
                    s.connect((bridge_info.ip_address, bridge_info.port))
                    response = s.recv(1024).decode('utf-8')
                    if response == "accept":
                        print(f"Connected to {interface.lan_name}")
                        connected = True
                         handle_station_tasks(interface, hosts)  # sends message to the destination and host
                    else:
                        print(f"Connection to {interface.lan_name} rejected")
            except socket.error as e:
                print(f"Error connecting to {interface.lan_name}: {e}")
                retry_count +=1
                time.sleep(retry_interval)
        else:
            print(f"Bridge information not found for {interface.lan_name}")


class RoutingTableEntry:
    def __init__(self, dest_network, next_hop, subnet_mask, interface):
        self.dest_network = dest_network
        self.next_hop = next_hop
        self.subnet_mask = subnet_mask
        self.interface = interface

def parse_routingtable_file(file_path):
    # Data Structure for storing routing_table_entries
    routing_table_entries = []
    with open(file_path, 'r') as file:
        for line in file:
            # Split each line into tokens
            tokens = line.strip().split()

            # Check if the line has at least four tokens (dest_network, next_hop, subnet_mask, interface)
            if len(tokens) >= 4:
                dest_network = tokens[0]
                next_hop = tokens[1]
                subnet_mask = tokens[2]
                interface = tokens[3]
                routing_entry = RoutingTableEntry(dest_network, next_hop, subnet_mask, interface)
                routing_table_entries.append(routing_entry)
    
    return routing_table_entries



def main_loop():
    
    
    while True:
        # Check for user input, incoming messages, and ARP requests
        # Process each type of event accordingly
        pass

