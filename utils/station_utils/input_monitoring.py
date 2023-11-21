import socket
import select
import sys
from utils.station_utils.station_parser import Interfaces,Interfaceparser

ifaceparser = Interfaceparser()


def check_mac_on_same_station(mac,ifaces)-> bool:
    for interface in ifaces:
        iface_dict = ifaceparser.interface_to_dict(interface)
        if mac == iface_dict['Mac Address']:
            return True
    return False

def check_valid_mac_format(mac):
    mac_split = mac.split(':')
    if len(mac_split) == 6 and mac_split[0] == 2:
        return True
    return False

def monitoring(connections: list, interface_file: str)-> None:

    interfaces = ifaceparser.parse_interface_file(interface_file)

    should_listen = True
    active_sockets = [info['Socket'] for info in connections]
    # interface_names = [info]
    prompt_displayed = False

    while should_listen:
        try:
            read_sockets, _, _ = select.select(active_sockets + [sys.stdin], [], [], .1)
            # Print the default message prompt
            if not prompt_displayed:
                sys.stdout.write("Enter message in format mac address: message. If no mac address no message will be sent\n")
                sys.stdout.write(">> ")
                sys.stdout.flush()  # Flush to ensure the message is immediately displayed
                prompt_displayed = True

            for sock in read_sockets:
                user_input = ''
                if sock == sys.stdin:
        
                    user_input = sys.stdin.readline().strip()
                    entered_mac = user_input[:17]
                    prompt_displayed = False
                    if check_valid_mac_format(entered_mac):
                        if not check_mac_on_same_station(entered_mac, interfaces):
                            if user_input:
                                    for bridge in active_sockets:
                                        bridge.send(user_input.encode())
                        else:
                            sys.stdout.write("Entered Mac Address is on this station\n")
                            sys.stdout.flush()
                    else:
                        sys.stdout.write("No valid Mac Address detected\n")
                        sys.stdout.flush()
                   
                
                else:
                    data = sock.recv(1024)
                    print(data)
                    if data:
                        if len(data) < 12:
                            print("Incomplete frame received, discarding.")
                            continue
        
        except socket.error as e:
            print(f"Socket error: {e}")

        except select.error as e:
            print(f"Select error: {e}")

        except KeyError as e:
            print(f"Key error: {e}")

        except Exception as e:
            print(f"An error occurred: {e}")
                