from utils.station_utils.network_init import parse_hostname_file, parse_routing_table_file, parse_interface_file,\
      print_forwarding_table, print_hosts, print_interfaces


def station(interface: str, routingtable: str, hostname: str)-> None:
    '''
    Parameters for station are the file names with the data for interfacee, routingtable, and hostname
    Params are received through command line arguments
    '''
    interfaces = parse_interface_file(interface)
    routing_tables = parse_routing_table_file(routingtable)
    hostnames = parse_hostname_file(hostname)

    print(f'\nInterfaces from file {interface}:\n')
    print_interfaces(interfaces)
    print(f'\nRouting Tables from file {routingtable}:\n')
    print_forwarding_table(routing_tables)
    print(f'\nHosts from file {hostname}:\n')
    print_hosts(hostnames)


if __name__ == '__main__':
    import os

    interface_file = os.path.abspath('./project/ifaces/ifaces.a')
    routingtable_file = os.path.abspath('./project/rtables/rtable.a')
    host_file = os.path.abspath('./project/hosts')
    station(interface_file, routingtable_file, host_file)