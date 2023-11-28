# Authors as22cq (Aditya Sugandhi) & apf19e (Andrew Franklin)
import json
import socket
import sys
import select
import threading
import time
import random as r
import argparse
from utils.bridge_utils.bridge_init import Bridge
from utils.bridge_utils.bridge_parser import Bridgeparser

MAX_CONNECTIONS = 10
PORT = r.randint(1000, 6000)
INACTIVE_TIMEOUT = 60

parser = argparse.ArgumentParser(description="Bridge file that takes input of the file name and creates sockets to listen to incoming connections")
parser.add_argument("name", help="Enter Station name")
args = parser.parse_args()
station_name = args.name
# station_name = 'cs1'
ip = '127.0.0.1'
B = Bridgeparser()
mac_port_mapping = {}
last_seen_times = {}
exit_signal = threading.Event()


def send_to_all(bridge_socket, bridge, client_address, user_input):
    for client_port in bridge.active_ports:
        if client_port != client_address:
            bridge_socket.sendto(user_input.encode(), (ip, client_port))
            print(f"Sending data to station on port {client_port}: {user_input}")


def handle_user_input(bridge):
    global exit_signal
    while not exit_signal.is_set():
        user_input = input("Enter your command: ")
        if user_input.lower() == "exit":
            exit_signal.set()
            break
        if user_input == 'getports':
            print(bridge.getportmap())


def start_server():
    global exit_signal
    bridge = Bridge(station_name, ip, PORT)

    bridge.bridge_socket.bind((ip, PORT))
    bridge.bridge_socket.listen(5)
    print(bridge.bridge_socket.getsockname())
    ip_addrr = bridge.bridge_socket.getsockname()[0]
    print(ip_addrr)
    bridge.bridge_socket.setblocking(0)

    print(f"Bridge Started Running on the:{PORT}, {ip_addrr}")
    print(station_name)

    print(bridge.getportmap())
    B.file_write(ip_addrr, PORT, str(station_name))
    bridge.promptdisplay()
    while not exit_signal.is_set():
        try:
            readable, _, _ = select.select([bridge.bridge_socket] + bridge.active_ports+ [sys.stdin], [], [], 1.0)  # 1.0 second timeout        

            for sock in readable:
                if sock == sys.stdin:
                    user_input = sys.stdin.readline().strip()
                    showprompt = False
                    waitstdin = False
                    if user_input == 'show sl':
                        bridge.show_port_mapping()
                    elif user_input == 'quit':
                        exit_signal.set()
                        break
                    else:
                        bridge.promptdisplay()

                
                
                elif sock == bridge.bridge_socket:
                    # New connection
                    client_socket, client_address = bridge.bridge_socket.accept()
                    print(client_socket)
                    if len(bridge.port_mapping) < MAX_CONNECTIONS:
                        client_socket.send('accept'.encode())
                        print(client_address[1], client_socket)
                        bridge.update_mapping(client_socket, int(client_address[1]))
                        print(f"Accepted connection from {client_address}")
                        bridge.active_ports.append(client_socket)
                        bridge.promptdisplay()
                    else:
                        client_socket.send('reject'.encode())
                        client_socket.send('Port are full'.encode())
                        print(f"Rejected connection from {client_address} as ports are full")

                    # Start the check connection status on a different thread
                    if not bridge.check_connection_status:
                        threading.Thread(target=bridge.check_connection_status).start()
                else:
                    # Existing client, handle data
                    try:
                        data = sock.recv(1024)
                        json_data = data.decode('utf-8')
                        data_received = json.loads(json_data)
                        # checks for metadata string, always from station.
                        if data_received['Message'] == 'metadata':
                            source_ip = data_received['Source IP']
                            source_mac = data_received['Source MAC']
                            bridge.update_macaddress(sock, source_mac)
                        else:
                            print(f"Received data from {bridge.port_mapping[sock]}: {json_data}")
                            bridge.handle_station_data(client_socket,json_data)
                        if not data:
                            print(f"Closing connection with {bridge.port_mapping[sock]}")
                            sock.close()
                            bridge.active_ports.remove(sock)
                            del bridge.port_mapping[sock]
                        
                    except Exception as e:
                        print(f"Error handling client {bridge.port_mapping[sock]}: {str(e)}")
                        sock.close()
                        bridge.active_ports.remove(sock)
                        del bridge.port_mapping[sock]
        except BlockingIOError:
            continue

    print('Exit signal received. Shutting down...')
    bridge.exit_signal.set()
    print('Removed line from file')
    B.remove_line_from_file(station_name)
    bridge.bridge_socket.close()
    print('Exiting...')


if __name__ == "__main__":
    try:
        bridges = B.parse_bridge_file()
        bridge_names = [bridge.name for bridge in bridges]

        if station_name not in bridge_names:
            main_thread = threading.Thread(target=start_server)
            main_thread.start()

            main_thread.join()
        else:
            print('Try another bridge name!')
    except KeyboardInterrupt:
        print("Ctrl+C detected. Exiting...")
        exit_signal.set()
        B.remove_line_from_file(station_name)
        main_thread.join()  # Wait for the main thread to finish
