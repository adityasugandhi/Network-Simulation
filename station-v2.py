# Authors as22cq (Aditya Sugandhi) & apf19e (Andrew Franklin)
from utils.station_utils.station_parser import  Stationparser,Interfaces
from utils.station_utils.lan_hooks import Lanhooks
import threading
import argparse
lhooks = Lanhooks()





def station(interface_file: str, host_file: str, rt_file: str)-> None:
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
    # print(lhooks.connect_to_all_lans())

    #lhooks.connect_to_bridge('127.0.0.1',,'test')
    connections = lhooks.connect_to_all_lans(interface_file, host_file, rt_file)

    
    #thread = threading.Thread(target=input_monitoring.monitoring, args=(connections))
   # thread.start()
    

def getarguments():
    parser = argparse.ArgumentParser(description='Description of your program')
    parser.add_argument('router', type=str, help='Router argument')
    parser.add_argument('interface', type=str, help='Interface argument')
    parser.add_argument('routingtable', type=str, help='Routing table argument')
    parser.add_argument('hostname', type=str, help='Hostname argument')

    args = parser.parse_args()
    return args.router, args.interface, args.routingtable, args.hostname
if __name__ == '__main__':
    import os
    router,interface,routingtable,hostname = getarguments()
    interface_file = os.path.abspath(interface)
    routingtable_file = os.path.abspath(routingtable)
    host_file = os.path.abspath(hostname)
    # sparser = Stationparser(interface_file,routingtable_file,host_file)
    station(interface_file, host_file, routingtable_file)
