
from bridge_init import Bridge

bridge_instance = Bridge()

def forward_packet(self,packet, in_port, ex_port, port_mapping):
    if in_port in self.port_mapping:
        # Forward packet to the corresponding ex_port
        ex_port = self.port_mapping[in_port]
        forward_to_port(packet,in_port,ex_port)
        # Update port_mapping with the received acknowledgement
        port_mapping[in_port] = ex_port
    else:
        # Forward packet to all ports
        update_mapping(self,source_address,in_port)
        for port in port_mapping.values():
            # Update port_mapping with the received acknowledgement
            port_mapping[in_port] = ex_port

def forward_to_all_ports(self, data_frame, in_port):
        # Forward the frame to all ports except the incoming port
        for port in self.get_all_ports():
            if port != in_port:
                self.forward_to_port(data_frame, in_port, port)


def forward_to_port(self, data_frame, in_port, ex_port):
        # Simulate forwarding the frame to a specific port
        print(f"Forwarding frame from port {in_port} to port {out_port}:")
        print(data_frame)
        print("")

        

forward_packet(packet, in_port, ex_port, port_mapping)
print(port_mapping)
