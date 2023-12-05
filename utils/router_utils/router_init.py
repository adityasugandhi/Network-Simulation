# Authors as22cq (Aditya Sugandhi) & apf19e (Andrew Franklin)
import socket
import selectors
import time

class Router:
    def __init__(self):
        self.connections = {}
        self.router = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.router.setblocking(False)

        self.selector = selectors.DefaultSelector()
        self.selector.register(self.router, selectors.EVENT_READ, data=None)

    def update_connections(self, bridge_address, bridge_port):
        self.connections[bridge_address] = {
            'bridge_port': bridge_port,
            'last_seen': time.time(),
            'mac_address': None
        }

    def getsockaddr(self, target_mac):
        for source_address, info in self.connections.items():
            if info['mac_address'] == target_mac:
                return source_address
        return None

    def connect_to_bridge(self, bridge_address, bridge_port):
        try:
            self.router.connect((bridge_address, bridge_port))
            print('-----Waiting for response-----')
            response = self.router.recv(1024).decode()
            if response == 'accept':
                print('-----Connection accepted-----')
                self.update_connections(bridge_address, bridge_port)
                return response
            else:
                return response
        except socket.error as e:
            # print(f"Error connecting to {bridge_address}:{bridge_port}: {e}")
            return "reject"

    def receive_packet(self):
        events = self.selector.select()
        for key, mask in events:
            if key.data is None:
                # This is the server socket (self.router) being ready to read
                client_socket, _ = key.fileobj.accept()
                client_socket.setblocking(False)
                self.selector.register(client_socket, selectors.EVENT_READ, data=b"")
            else:
                # This is a client socket being ready to read
                client_socket = key.fileobj
                data = client_socket.recv(1024).decode()
                
                # Process the received data as needed
                sender_mac = data[0]
                if sender_mac in self.connections:
                    bridge_socket = self.getsockaddr(sender_mac)
                    bridge_socket.send(data)
                    # Update last_seen time for the sender
                    self.connections[sender_mac]['last_seen'] = time.time()

                # Check for Acknowledge
                ack_data = 'Acknowledge'
                client_socket.send(ack_data.encode())
                print('Acknowledge sent')




if __name__ == "__main__":
    router = Router()
    router.router

    server_host = 'your_host'  # Replace with your actual host
    server_port = 0000  # Replace with your actual port

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((server_host, server_port))
    server_socket.listen()

    # print(f"Router listening on {server_host}:{server_port}")

    server_socket.setblocking(False)
    router.selector.register(server_socket, selectors.EVENT_READ, data=None)

    try:
        while True:
            router.receive_packet()
    except KeyboardInterrupt:
        print("Router shutting down.")
    finally:
        router.selector.close()
    # Add code to set up the server socket for incoming connections
    # server_socket.bind(('your_host', your_port))
    # server_socket.listen()
    
    while True:
        router.receive_packet()
