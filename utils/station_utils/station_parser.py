# Authors as22cq (Aditya Sugandhi) & apf19e (Andrew Franklin)
from ..settings import interface_file, routingtable_file, host_file
import ipaddress



import ipaddress

def is_ip_in_range(ip_str, subnet_mask_str, ip_to_check):
    # Convert the IP address and subnet mask strings to IPv4Address and IPv4Network objects
    ip = ipaddress.IPv4Address(ip_str)
    subnet_network = ipaddress.IPv4Network(subnet_mask_str, strict=False)

    # Calculate the network address
    network_address = ipaddress.IPv4Address(subnet_network.network_address)

    # Calculate the first and last usable IP addresses
    start_ip = network_address + 1  # Skip the network address itself
    end_ip = network_address + (2 ** (32 - subnet_network.prefixlen)) - 2

    # Convert the IP address to check to an IPv4Address object
    ip_to_check_ipv4 = ipaddress.IPv4Address(ip_to_check)

    # Check if the IP to check falls within the calculated range
    return start_ip <= ip_to_check_ipv4 <= end_ip



def ip_to_int(ip):
    # Convert IP address to integer representation
    parts = [int(part) for part in ip.split('.')]
    return (parts[0] << 24) + (parts[1] << 16) + (parts[2] << 8) + parts[3]

class Stationparser:
    def __init__(self):
        self.interface_file = interface_file
        self.routingtable_file = routingtable_file
        self.host_file = host_file
    
    
class Interfaces:
    def __init__(self,name, ip_address, subnet_mask, mac_address, lan_name):
        #super().__init__()
        self.name = name
        self.ip_address = ip_address
        self.subnet_mask = subnet_mask
        self.mac_address = mac_address
        self.lan_name = lan_name

class Interfaceparser:
    def __init__(self):
         #super().__init__()
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
    
    def list_of_iface_dicts(self,ifaces):
        return [self.interface_to_dict(iface) for iface in ifaces]
    

    def show_ifaces(self, interfaces):
        names = []
        ips = []
        subnets = []
        macs = []
        lans = []
        for iface in interfaces:
            names.append(iface.name)
            ips.append(iface.ip_address)
            subnets.append(iface.subnet_mask)
            macs.append(iface.mac_address)
            lans.append(iface.lan_name)

        output = 'Interfaces Table'
        output += "{:<10} {:<15} {:<15} {:<15} {:<10}\n".format("Name", "IP Address", 'Subnet Mask', 'Mac Address', 'Lan Name')

        for iface in interfaces:
            output += "{:<1} {:<15} {:<15} {:<15} {:<10}\n".format(iface.name, iface.ip_address, iface.subnet_mask, iface.mac_address, iface.lan_name)

        return output

        # ifaces_df = pd.DataFrame({
        #     'Name': names,
        #     'IP Address': ips,
        #     'Subnet Mask': subnets,
        #     'Mac Address': macs,
        #     'Lan Name': lans 
        # })

        # print('Interface Table:')
        # print(ifaces_df)

    def bridge_forwarding_info(self, interfaces, forwarding_interface):
        for iface in interfaces:
            if iface.name == forwarding_interface:
                return iface.ip_address, iface.mac_address, iface.lan_name
        return None

    
class Routingtable:
    def __init__(self,dest_network,next_hop_ip,network_mask,network_interface):
        #super().__init__()
        self.dest_network = dest_network
        self.next_hop_ip = next_hop_ip
        self.network_mask = network_mask
        self.network_interface = network_interface


class Routingparser:
    def __init__(self):
        pass
         #super().__init__()

    def parse_routing_table_file(self, rt_file):
        routing_table = []
        with open(rt_file, 'r') as file:
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
    
    def show_routing_table(self, routing_table):
        # print('Routing Table:')
        # print('Destination Network \t Next Hop IP \t Network Mask \t Network Interface')
        # for tb in routing_table:
        #     print(f'{tb.dest_network} \t {tb.next_hop_ip} \t {tb.network_mask} \t {tb.network_interface}')

        output = 'Routing Table'
        output += "{:<15} {:<15} {:<15} {:<15}\n".format("Destination Network", "Next Hop IP", 'Network Mask', 'Network Interface')

        for tb in routing_table:
            output += "{:<15} {:<15} {:<15} {:<15}\n".format(tb.dest_network, tb.next_hop_ip, tb.network_mask, tb.network_interface)

        return output

    def default_ip_gateway_next_hop_interface(self,routes):
        for route in routes:
            if route.dest_network == '0.0.0.0':
                return route.network_interface
        return None
    
    def is_ip_in_range(self,start_ip, netmask,ip):
        try:
            ip_network = ipaddress.IPv4Network("{}/{}".format(start_ip, netmask), strict=False)
            return ipaddress.IPv4Address(ip) in ip_network
        except ValueError:
            return False 
        
    def get_next_hop_interface(self, dest_ip, routes):
        for route in routes:
            # if route.dest_network == dest_ip:
            #     return route.network_interface
            if self.is_ip_in_range(route.dest_network, route.network_mask, dest_ip):
                return route.network_interface
        return self.default_ip_gateway_next_hop_interface(routes)




class Host():
    def __init__(self,name, ip_address):
       # super().__init__()
        self.name = name
        self.ip_address = ip_address



class HostParser():
    def __init__(self):
        #super().__init__()
        pass
        

    def parse_hostname_file(self, host_file):
        hosts = []
        with open(host_file, 'r') as file:
            for line in file:
                # Split each line into tokens
                tokens = line.strip().split()

                # Check if the line has at least two tokens (name and IP address)
                if len(tokens) >= 2:
                    name = tokens[0]
                    ip_address = tokens[1]
                    host = Host(name, ip_address)
                    hosts.append(host)

        self.host_list = hosts
        return hosts  # Save the parsed hosts in the object's host_list
        
    

    def show_hosts(self,hosts):
        
        output = "Hosts Table:\n"
        output += "{:<10} {:<15}\n".format("Name", "IP Address")

        for host in hosts:
            output += "{:<10} {:<15}\n".format(host.name, host.ip_address)

        return output

    def get_host_ip(self, hosts, name):
        for host in hosts:
            if host.name == name:
                return host.ip_address
            
        return None
    
    def get_host_from_ip(self, hosts, ip):
        for host in hosts:
            if host.ip_address == ip:
                return host.name
            
        return None
