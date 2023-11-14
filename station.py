import socket
import time
from ipaddress import IPv4Address
import netifaces

# Get MAC address of a specific network interface (e.g., 'eth0')
station_mac = netifaces.ifaddresses('eth0')[netifaces.AF_LINK][0]['addr']
print(f"Station's MAC address: {station_mac}")

next_hop_ipaddr = '192.168.1.1'  # Example IP address for the next hop
dst_ipaddr = '192.168.1.10'     # Example IP address for the final destination

# Constants for packet types
TYPE_IP_PKT = 1
TYPE_ARP_PKT = 0

# Structure for ARP packet
class ARP_PKT:
    def __init__(self, op, srcip, srcmac, dstip, dstmac):
        self.op = op
        self.srcip = srcip
        self.srcmac = srcmac
        self.dstip = dstip
        self.dstmac = dstmac

# Structure for IP packet
class IP_PKT:
    def __init__(self, dstip, srcip, protocol, sequenceno, length, data):
        self.dstip = dstip
        self.srcip = srcip
        self.protocol = protocol
        self.sequenceno = sequenceno
        self.length = length
        self.data = data

# ARP cache as a list
arp_cache = []

# Structure for pending packets
class PendingPacket:
    def __init__(self, next_hop_ipaddr, dst_ipaddr, pending_pkt):
        self.next_hop_ipaddr = next_hop_ipaddr
        self.dst_ipaddr = dst_ipaddr
        self.pending_pkt = pending_pkt

pending_queue = []
def construct_arp_request(arp_pkt, next_hop_router_ip):
    arp_request = ARP_PKT(
        op=0,  # ARP request
        srcip=arp_pkt.srcip,
        srcmac=station_mac,  # Replace with the station's MAC address
        dstip=next_hop_router_ip,
        dstmac="FF:FF:FF:FF:FF:FF"  # Broadcasting ARP request to router MAC
    )
    return arp_request

def send_arp_request_to_router(arp_request):
    # Send the constructed ARP request to the router
    # Construct the Ethernet frame
    ether_frame = construct_ether_frame(arp_request)

    # Use socket or appropriate method to send the Ethernet frame to the router
    send_ether_frame_to_router(ether_frame)
def send_ether_frame_to_router(ether_frame):
    try:
        # Create a raw socket to send the Ethernet frame
        with socket.socket(socket.AF_PACKET, socket.SOCK_RAW) as s:
            s.bind(('eth0', 0))  # Replace 'eth0' with the relevant network interface
            s.send(ether_frame)
            print("ARP request sent to the router")
    except socket.error as e:
        print(f"Error sending ARP request to the router: {e}")
def get_next_hop_router_ip(destination_ip):
    if destination_ip not in local_subnet:
        return predefined_router_ip  # Replace with the actual router IP
    return None  # No router needed for local subnet
def construct_ether_frame(arp_response):
    # Construct an Ethernet frame for the ARP response
    # Construct the frame with destination MAC, source MAC, and EtherType for ARP (0x0806)
    dst_mac = arp_response.dstmac
    src_mac = station_mac  # Replace with the station's MAC address
    ethertype = 0x0806  # ARP EtherType
    ether_header = dst_mac + src_mac + ethertype.to_bytes(2, byteorder='big')
    arp_pkt_data = construct_arp_packet(arp_response)

    return ether_header + arp_pkt_data
def construct_arp_packet(arp_response):
    op_code = arp_response.op  # ARP operation (0 for request, 1 for response)
    src_ip = arp_response.srcip
    src_mac = arp_response.srcmac
    dst_ip = arp_response.dstip
    dst_mac = arp_response.dstmac

    # Constructing the ARP response packet
    arp_op = op_code.to_bytes(2, byteorder='big')  # Convert op code to 2 bytes
    src_ip_bytes = src_ip.to_bytes(4, byteorder='big')  # Source IP as 4 bytes
    src_mac_bytes = b''.join(bytes([int(x, 16)]) for x in src_mac.split(':'))  # Source MAC in bytes
    dst_ip_bytes = dst_ip.to_bytes(4, byteorder='big')  # Destination IP as 4 bytes
    dst_mac_bytes = b''.join(bytes([int(x, 16)]) for x in dst_mac.split(':'))  # Destination MAC in bytes

    # Construct the ARP packet by concatenating all necessary fields
    arp_packet = arp_op + src_mac_bytes + src_ip_bytes + dst_mac_bytes + dst_ip_bytes

    return arp_packet

def send_arp_response(arp_response):
    # Construct the Ethernet frame with the ARP response packet
    ether_pkt = construct_ether_frame(arp_response)

    # Send the Ethernet frame over a raw socket
    try:
        # Replace 'eth0' with the relevant network interface
        with socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(3)) as s:
            s.bind(('eth0', socket.htons(3)))  # Bind to the interface for sending ARP (htons(3) for ARP)
            s.send(ether_pkt)  # Send the constructed ARP response
            print(f"ARP response sent to {arp_response.dstip}")
    except socket.error as e:
        print(f"Error sending ARP response: {e}")

def forward_arp_request(arp_pkt):
    next_hop_router_ip = get_next_hop_router_ip(arp_pkt.dstip)
    if next_hop_router_ip:
        arp_request = construct_arp_request(arp_pkt, next_hop_router_ip)
        send_arp_request_to_router(arp_request)
    else:
        print("Next-hop router for forwarding ARP request not found.")

def parse_hostname_file(hostname_file):
    host_ip_map = {}
    try:
        with open(hostname_file, 'r') as file:
            lines = file.readlines()
            for line in lines:
                parts = line.split()
                if len(parts) == 2:
                    host, ip = parts
                    host_ip_map[host] = ip
                else:
                    print(f"Skipping line: {line}. Incorrect format.")
    except FileNotFoundError:
        print("Hostname file not found.")
    return host_ip_map

def parse_interface_file(interface_file):
    interface_info = {}
    try:
        with open(interface_file, 'r') as file:
            lines = file.readlines()
            for line in lines:
                parts = line.split()
                if len(parts) == 5:
                    interface, ip, subnet, mac, lan = parts
                    interface_info[interface] = {
                        'ip': ip,
                        'subnet': subnet,
                        'mac': mac,
                        'lan': lan
                    }
                else:
                    print(f"Skipping line: {line}. Incorrect format.")
    except FileNotFoundError:
        print("Interface file not found.")
    return interface_info

def establish_connections(interface_info):
    socket_connections = {}
    for interface, details in interface_info.items():
        connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        bridge_address = details['ip']  # Get the bridge IP from interface details
        bridge_port = 12345  # Placeholder for the bridge port, use the actual port

        try:
            connection.connect((bridge_address, bridge_port))
            connection.send(b'Station connecting')

            response = connection.recv(1024).decode()
            if response == "accept":
                socket_connections[interface] = connection
            else:
                print(f"Connection to {bridge_address} rejected.")
                connection.close()
        except (socket.error, ConnectionRefusedError) as e:
            print(f"Error connecting to {bridge_address}: {e}")
            connection.close()

        time.sleep(2)  # Add a delay before attempting the next connection
    return socket_connections

def handle_arp_packet(received_packet):
    arp_pkt = received_packet  # Rename for clarity

    if arp_pkt.op == 0:  # ARP request
        if arp_pkt.dstip == IPv4Address('127.0.0.1'):
            # It's an ARP request for the station's own IP, prepare an ARP response
            # Construct the ARP response packet
            arp_response = ARP_PKT(
                op=1,  # ARP response
                srcip=IPv4Address('127.0.0.1'),
                srcmac=station_mac,  # Replace with the station's MAC address
                dstip=arp_pkt.srcip,
                dstmac=arp_pkt.srcmac
            )
            # Send the ARP response packet
            send_arp_response(arp_response)
        else:
            # It's an ARP request for a different IP, handle accordingly
            if arp_pkt.dstip in local_subnet:  # Check if IP is in the local subnet
    # ARP is for a different IP within the local subnet, send appropriate response
                if arp_pkt.dstip in arp_cache:  # If MAC address for IP is already in ARP cache
        # If the MAC address for the requested IP is known, prepare an ARP response
                    mac_address = arp_cache[arp_pkt.dstip]
                    arp_response = ARP_PKT(
                        op=1,  # ARP response
                        srcip=arp_pkt.dstip,
                        srcmac=mac_address,  # Respond with known MAC address for the requested IP
                        dstip=arp_pkt.srcip,
                        dstmac=arp_pkt.srcmac
                    )
                    # Send the constructed ARP response
                    send_arp_response(arp_response)
                else:
                    # If MAC address for the IP is not known, handle this scenario accordingly
                    # For instance, forward the ARP request to a router
                    forward_arp_request(arp_pkt)  # Forward the ARP request to the router
    elif arp_pkt.op == 1:  # ARP response
        # It's an ARP response, update the ARP cache
        update_arp_cache(arp_pkt.srcip, arp_pkt.srcmac)
        # Process pending packets, checking if they can be sent now
        resend_pending_packets()
    else:
        # Unknown ARP packet type
        print("Unknown ARP packet type.")

def update_arp_cache(ip, mac):
    # Implement ARP cache update
    arp_cache.append((ip, mac))

def add_to_pending_queue(dest_ip, message):
    # Add pending packets to the queue
    pending_queue.append(PendingPacket(next_hop_ipaddr, dst_ipaddr, message))

def resend_pending_packets():
    for packet in pending_queue:
        for ip, mac in arp_cache:
            if packet.next_hop_ipaddr == ip:
                # Send the pending packet using the socket connection
                # Replace this placeholder with your logic to send the packet
                try:
                    socket_connection = socket_connections[packet.dest_ip]
                    socket_connection.send(packet.pending_pkt.encode())
                    print(f"Resending pending packet to {packet.dest_ip}")
                except (KeyError, socket.error) as e:
                    print(f"Error sending packet to {packet.dest_ip}: {e}")
                break  # Break once the packet is sent



# Main functionality
if __name__ == "__main__":
    hostname_file = "hostname.txt"
    interface_file = "./project/ifaces/ifaces.a"

    hostname_info = parse_hostname_file(hostname_file)
    interface_info = parse_interface_file(interface_file)

    socket_connections = establish_connections(interface_info)

    while True:
        # Code to handle user input
        # Code to process received messages
        # Code for handling ARP requests and replies
        # Code for managing pending packets
        time.sleep(1)  # Placeholder for continuous operation
