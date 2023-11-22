
import socket
import select
import time
import threading
import random as r
import argparse
import concurrent.futures
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
last_seen_times = {}
exit_signal = threading.Event()


def send_to_all(bridge_socket,bridge,client_address,user_input):
    for client_port in bridge.active_ports:
        if client_port != client_address:
            bridge_socket.sendto(user_input.encode(), (ip, client_port))
            print(f"Sending data to station on port {client_port}: {user_input}")

    

def handle_user_input():
    global exit_signal
    while not exit_signal.is_set():
        user_input = input("Enter your command: ")
        if user_input.lower() == "exit":
            exit_signal.set()
    


def handle_client(client_socket, client_port):
    print('start sending data')
    while True:
        print('In the loop')
        data = client_socket.recv(1024).decode("utf-8") # This is a blocking call
        if not data:
            print(f"Client on port {client_port} disconnected. Waiting for data...")
            continue
        print(f"Received data from station on port {client_port}: {data}")

# Rest of the code remains unchanged
          

def handle_station_data(client_socket):
    
    while not exit_signal.is_set():
        try:
            # Check if there is data available to be read
            readable, _, _ = select.select([client_socket], [], [], 1.0)  # 1.0 second timeout
            if client_socket in readable:
                data = client_socket.recv(1024)
                if not data:
                    # Connection closed by the client
                    print(f"Connection closed by {client_socket.getpeername()}")
                    break
                else:
                    # Process the received data
                    print(f"Received data from {client_socket.getpeername()}: {data.decode()}")
            else:
                # No data available, do something else or continue waiting
                pass
        except BlockingIOError:
            # Handle the case where there is no data to read
            pass
        except Exception as e:
            print(f"Error receiving data: {e}")
            
            # Handle other exceptions if necessary
            break
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

    
    while not exit_signal.is_set():
        readable, _, _ = select.select([bridge.bridge_socket], [], [], 1.0)  # 1.0 second timeout

        if bridge.bridge_socket in readable:
            client_socket, client_address = bridge.bridge_socket.accept()
            client_socket.send('accept'.encode())
            bridge.update_mapping(client_socket,client_address[1])
            print(f"Accepted connection from {client_address}")
            bridge.active_ports.append(client_socket)

            # Start a new thread to handle messages from this client
            threading.Thread(target=handle_station_data, args=(client_socket,)).start()
    
    else:
        print('Exit signal received. Shutting down...')
        bridge.bridge_socket.close()
        B.remove_line_from_file(station_name)
        print('Removed line from file')
        print('Exiting...')
   


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
        main_thread.join() # Wait for the main thread to finish

#
#This code is a bridge server that listens for incoming connections from other bridge servers. It uses a thread pool to handle multiple connections simultaneously. The `handle_station_data` function is responsible for receiving and processing data from connected stations. The `handle_user_input` function allows the user to send messages to all connected stations. The server also handles exceptions such as socket errors and keyboard interrupts.