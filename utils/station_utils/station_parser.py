class Stationparser:
    def __init__(self,interface_file,routingtable_file,host_file) -> None:
        self.interface_file = interface_file
        self.routingtable_file = routingtable_file
        self.host_file = host_file
    
    
class Interfaces(Stationparser):
    def __init__(self,name,ip_address,subnet_mask,mac_address,lan_name) -> None:
        super().__init__()
        self.name = name
        self.ip_address = ip_address
        self.subnet_mask = subnet_mask
        self.mac_address = mac_address
        self.lan_name = lan_name
    
    def parse_interface_file(self):
        interfaces = []
        with open(self.interface_file, 'r') as file:
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
    def to_dict(self):
        return {
            'Name': self.name,
            'IP Address': self.ip_address,
            'Subnet Mask': self.subnet_mask,
            'Mac Address': self.mac_address,
            'Lan Name': self.lan_name
        }


        
        return interfaces
class Routingtable(Stationparser):
    def __init__(self,dest_network,next_hop_ip,network_mask,network_interface) -> None:
        super().__init__()
        self.dest_network = dest_network
        self.next_hop_ip = next_hop_ip
        self.network_mask = network_mask
        self.network_interface = network_interface

    def parse_routing_table_file(file_path: str):
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
                    
                    forward_table = Routingtable(dest_network, next_hop_ip, network_mask, network_interface)
                    routing_table.append(forward_table)
        return routing_table
