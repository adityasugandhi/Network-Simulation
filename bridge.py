import socket
import select
import time
import threading
import random as r
import argparse
from utils.bridge_utils.bridge_init import Bridge
from utils.bridge_utils.bridge_parser import Bridgeparser

MAX_CONNECTIONS = 10
PORT = r.randint(1000, 6000)
INACTIVE_TIMEOUT = 60

parser = argparse.ArgumentParser(description="Bridge file that takes input of file name and creates sockets to listen to incoming connections")
parser.add_argument("name", help="Enter Station name")
args = parser.parse_args()
station_name = args.name
#station_name = 'cs1'
ip = '127.0.0.1'
B = Bridgeparser()
mac_port_mapping = {}
active_ports = []
last_seen_times = {}
exit_signal = threading.Event()

def handle_user_input():
    global exit_signal
    while not exit_signal.is_set():
        user_input = input("Enter your command: ")
        if user_input.lower() == "exit":
            exit_signal.set()
        if user_input == 'active_ports':
            print(active_ports)

def handle_client(client_socket):
    data = client_socket.recv(1024)
    client_socket.send(b"Received your data.")
    client_socket.close()

def start_server():
    global exit_signal
    bridge_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    bridge_socket.bind((ip, PORT))
    bridge_socket.listen(5)
    print(bridge_socket.getsockname())
    ip_addrr = bridge_socket.getsockname()[0]
    print(ip_addrr)
    bridge_socket.setblocking(0)

    print(f"Bridge Started Running on the:{PORT}, {ip_addrr}")
    bridge = Bridge(station_name, ip, PORT)
    print(station_name)

    print(bridge.getportmap())
    B.file_write(ip_addrr, PORT, str(station_name))

    inputs = [bridge_socket]  # Add bridge_socket to the list of inputs

    while not exit_signal.is_set():
        try:
            read_sockets, _, _ = select.select(inputs, [], [], 1)  # Set a timeout

            for sock in read_sockets:
                #print(read_sockets)
                # print ('Bridge is running.')
                if sock is bridge_socket:
                    conn, addr = bridge_socket.accept()

                    inputs.append(conn)  # Add the new connection to the list of inputs
                    client_address, client_port = addr
                    print(f"New connection from {client_address}:{client_port}")
                    active_ports.append(client_port)
                    bridge.update_mapping(client_address, client_port)
                    print(bridge.getportmap())

                    if len(active_ports) < MAX_CONNECTIONS:
                        active_ports.append(conn)
                        print(f"New station connected-{conn}")
                        conn.send("accept".encode())
                        # mac_address = conn.recv(1024).decode()
                        # bridge.update_mapping(mac_address, client_port)
                        # print(f"get map{bridge.getportmap()}")
                    # else:
                    #     conn.send("reject".encode())
                    #     conn.close()
                # else:
                #     data = sock.recv(1024)

                #     if data:
                #         if len(data) < 12:
                #             print("Incomplete frame received, discarding.")
                #             continue

            current_time = time.time()
            inactive_stations = [mac for mac, last_seen in last_seen_times.items() if current_time - last_seen > INACTIVE_TIMEOUT]
            for mac in inactive_stations:
                del mac_port_mapping[mac]
                del last_seen_times[mac]

        except socket.error as e:
            print(f"Socket error: {e}")
            read_sockets, _, _ = select.select(inputs + active_ports, [], [], 1)
            print(read_sockets)
            B.remove_line_from_file(station_name)
            bridge_socket.close()

        except select.error as e:
            print(f"Select error: {e}")

        except KeyboardInterrupt:
            print("Ctrl+C detected. Exiting...")
            exit_signal.set()

        except Exception as e:
            print(f"An error occurred: {e}")

    print("Closing the server.")
    B.remove_line_from_file(station_name)
    bridge_socket.close()

if __name__ == "__main__":
    try:
        bridges = B.parse_bridge_file()
        bridge_names = [bridge.name for bridge in bridges]
        bridge_addr = [bridge.ip_address for bridge in bridges]
        print(bridge_addr)

        if station_name not in bridge_names:
            user_input_thread = threading.Thread(target=handle_user_input)
            user_input_thread.start()

            main_thread = threading.Thread(target=start_server)
            main_thread.start()

            user_input_thread.join()
            main_thread.join()
        else:
            print('Try another bridge name!')
    except KeyboardInterrupt:
        print("Ctrl+C detected. Exiting...")
        exit_signal.set()
        main_thread.join()  # Wait for the main thread to finish
