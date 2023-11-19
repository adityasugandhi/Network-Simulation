import socket
import pickle
import threading
from bridge_init import 


def receive_frame(self, port):
        # Simulate continuously receiving frames on a specific port
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', port))
            s.listen()

            while True:
                conn, addr = s.accept()
                threading.Thread(target=self.handle_connection, args=(conn,)).start()