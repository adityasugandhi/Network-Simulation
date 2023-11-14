import socket
import select
import time
import os

MAX_CONNECTIONS = 10
PORT = 5555
INACTIVE_TIMEOUT = 60  # Seconds for inactivity timeout

mac_port_mapping = {}
active_ports = []
last_seen_times = {}

bridge_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
bridge_socket.bind(('localhost', PORT))
bridge_socket.listen(5)
bridge_socket.setblocking(0)

def process_data_frame(data):
    source_mac = data[:6]
    dest_mac = data[6:12]
    frame = data[12:]
    return source_mac, dest_mac, frame

def main():
    while True:
        try:
            read_sockets, _, _ = select.select([bridge_socket] + active_ports, [], [], 1)

            for sock in read_sockets:
                if sock is bridge_socket:
                    conn, addr = bridge_socket.accept()
                    if len(active_ports) < MAX_CONNECTIONS:
                        active_ports.append(conn)
                        print("New station connected")
                        conn.send("accept".encode())
                    else:
                        conn.send("reject".encode())
                        conn.close()
                else:
                    data = sock.recv(1024)
                    if data:
                        if len(data) < 12:
                            print("Incomplete frame received, discarding.")
                            continue

                        source_mac, dest_mac, frame = process_data_frame(data)

                        if len(frame) == 0:
                            print("Empty frame received, discarding.")
                            continue

                        if source_mac not in mac_port_mapping:
                            mac_port_mapping[source_mac] = sock
                            last_seen_times[source_mac] = time.time()
                        else:
                            last_seen_times[source_mac] = time.time()

                        if dest_mac not in mac_port_mapping:
                            mac_port_mapping[dest_mac] = None

                        for port in active_ports:
                            if port is not sock:
                                port.send(frame)

            current_time = time.time()
            inactive_stations = [mac for mac, last_seen in last_seen_times.items() if current_time - last_seen > INACTIVE_TIMEOUT]
            for mac in inactive_stations:
                del mac_port_mapping[mac]
                del last_seen_times[mac]

        except socket.error as e:
            print(f"Socket error: {e}")

        except select.error as e:
            print(f"Select error: {e}")

        except KeyError as e:
            print(f"Key error: {e}")

        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    

    ip_address = socket.gethostbyname(socket.gethostname())
    with open("ip_address_link", "w") as file:
        file.write(ip_address)


    with open("port_number_link", "w") as file:
        file.write(str(PORT))

    try:
        main()
    except KeyboardInterrupt:
        bridge_socket.close()
        print("Bridge closed")
