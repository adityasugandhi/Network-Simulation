
class Host:
    def __init__(self, name, ip_address):
        self.name = name
        self.ip_address = ip_address

    def to_dict(self):
        return {
            'Name': self.name,
            'IP Address': self.ip_address
        }


def parse_hostname_file(file_path: str) -> list[Host]:
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

def print_hosts(hosts: list[Host])-> None:
    for host in hosts:
        print(f'Name: {host.name}, IP Address: {host.ip_address}')


class ForwardingTable:
    def __init__(self, dest_network, next_hop_ip, network_mask, network_interface):
        self.dest_network = dest_network
        self.next_hop_ip = next_hop_ip
        self.network_mask = network_mask
        self.network_interface = network_interface

    def get_default_router(self):
        if self.dest_network == '0.0.0.0':
            return self.next_hop_ip
        return None
    
    def is_same_lan(self):
        if self.next_hop_ip == '0.0.0.0':
            return True
        return False
    
    def to_dict(self):
        return {
            'Dest Network': self.dest_network,
            'Next Hop IP': self.next_hop_ip,
            'Network Mask': self.network_mask,
            'Network Interface': self.network_interface
        }
    

def parse_routing_table_file(file_path: str) -> list[ForwardingTable]:
    routing_table = []
    with open(file_path, 'r') as file:
        for line in file:
            # Split each line into tokens
            tokens = line.strip().split()

            # Check if the line has at least three tokens (dest_network, next_hop_ip, network_mask, network_interface)
            if len(tokens) >= 4:
                dest_network = tokens[0]
                next_hop_ip = tokens[1]
                network_mask = tokens[2]
                network_interface = tokens[3]
                
                forward_table = ForwardingTable(dest_network, next_hop_ip, network_mask, network_interface)
                routing_table.append(forward_table)
    return routing_table


def print_forwarding_table(tbs: list[ForwardingTable])-> None:
    for tb in tbs:
        print(f'Destination Network: {tb.dest_network}, Next Hop IP: {tb.next_hop_ip}, Network Mask: {tb.network_mask}, Network Interface: {tb.network_interface}')


class Interface:
    def __init__(self, name, ip_address, subnet_mask, mac_address, lan_name):
        self.name = name
        self.ip_address = ip_address
        self.subnet_mask = subnet_mask
        self.mac_address = mac_address
        self.lan_name = lan_name

    def to_dict(self):
        return {
            'Name': self.name,
            'IP Address': self.ip_address,
            'Subnet Mask': self.subnet_mask,
            'Mac Address': self.mac_address,
            'Lan Name': self.lan_name
        }


def parse_interface_file(file_path: str) -> list[Interface]:
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

def print_interfaces(interfaces: list[Interface])-> None:
    for interface in interfaces:
        print(f'Name: {interface.name}, IP Address: {interface.ip_address}, Network Mask: {interface.subnet_mask}, Ethernet Address: {interface.mac_address}, LAN: {interface.lan_name}')


