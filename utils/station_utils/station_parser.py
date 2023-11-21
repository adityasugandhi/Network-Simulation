from ..settings import interface_file, routingtable_file, host_file

class Stationparser:
    def __init__(self) -> None:
        self.interface_file = interface_file
        self.routingtable_file = routingtable_file
        self.host_file = host_file
    
    
class Interfaces(Stationparser):
    def __init__(self,name, ip_address, subnet_mask, mac_address, lan_name) -> None:
        super().__init__()
        self.name = name
        self.ip_address = ip_address
        self.subnet_mask = subnet_mask
        self.mac_address = mac_address
        self.lan_name = lan_name

class Interfaceparser(Stationparser):
    def __init__(self):
         super().__init__()
         self.last_interface_instance = None  
    def parse_interface_file(self, interface_file):
        interfaces = []
        with open(interface_file, 'r') as file:
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
                    interface = Interfaces(name, ip_address, subnet_mask, mac_address, lan_name)
                    interfaces.append(interface)
                    self.last_interface_instance = interface  # 
        return interfaces
                        
    def to_dict(self):
        if self.last_interface_instance is not None:
            return {
                'Name': self.last_interface_instance.name,
                'IP Address': self.last_interface_instance.ip_address,
                'Subnet Mask': self.last_interface_instance.subnet_mask,
                'Mac Address': self.last_interface_instance.mac_address,
                'Lan Name': self.last_interface_instance.lan_name
            }
        else:
            return {}
    
    def interface_to_dict(self, iface):
        return {
            'Name': iface.name,
            'IP Address': iface.ip_address,
            'Subnet Mask': iface.subnet_mask,
            'Mac Address': iface.mac_address,
            'Lan Name': iface.lan_name
        }
    
class Routingtable(Stationparser):
    def __init__(self,dest_network,next_hop_ip,network_mask,network_interface) -> None:
        super().__init__()
        self.dest_network = dest_network
        self.next_hop_ip = next_hop_ip
        self.network_mask = network_mask
        self.network_interface = network_interface

    def parse_routing_table_file(self):
        routing_table = []
        with open(self.routingtable_file, 'r') as file:
            for line in file:
                # Split each line into tokens
                tokens = line.strip().split()

                # Check if the line has at least three tokens (dest_network, next_hop_ip, network_mask, network_interface)
                if len(tokens) >= 4:
                    dest_network = tokens[0]
                    next_hop_ip = tokens[1]
                    network_mask = tokens[2]
                    network_interface = tokens[3]
                    
                    forward_table = Routingtable(dest_network, next_hop_ip, network_mask, network_interface)
                    routing_table.append(forward_table)
        return routing_table


class Host(Stationparser):
    def __init__(self, name, ip_address):
        super().__init__()
        self.name = name
        self.ip_address = ip_address

    def to_dict(self):
        return {
            'Name': self.name,
            'IP Address': self.ip_address
        }


    def parse_hostname_file(self):
        hosts = []
        with open(self.host_file, 'r') as file:
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
