
from utils.station_utils.station_parser import  Stationparser,Interfaces
from utils.station_utils.lan_hooks import Lanhooks

lhooks = Lanhooks()
def station()-> None:
    '''
    Parameters for station are the file names with the data for interfacee, routingtable, and hostname
    Params are received through command line arguments
    '''
    # interfaces = parse_interface_file(interface)
    # routing_tables = parse_routing_table_file(routingtable)
    # hostnames = parse_hostname_file(hostname)

    # print(f'\nInterfaces from file {interface}:\n')
    # print_interfaces(interfaces)
    # print(f'\nRouting Tables from file {routingtable}:\n')
    # print_forwarding_table(routing_tables)
    # print(f'\nHosts from file {hostname}:\n')
    # print_hosts(hostnames)
    print(lhooks.connect_to_all_lans())

    #lhooks.connect_to_bridge('127.0.0.1',,'test')
   # connections = lan_hooks.connect_to_all_lans(interfaces)
    
    #input_monitoring.monitoring(connections)



if __name__ == '__main__':
    import os

    # interface_file = os.path.abspath('./project/ifaces/ifaces.a')
    # routingtable_file = os.path.abspath('./project/rtables/rtable.a')
    # host_file = os.path.abspath('./project/hosts')
    # sparser = Stationparser(interface_file,routingtable_file,host_file)
    station()
