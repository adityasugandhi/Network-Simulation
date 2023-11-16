import ipaddress

BRIDGE_FILE_PATH = 'utils/station_utils/bridge.txt'

def increment_ip(ip_address):
    # Convert the IP address string to an IPv4Address object
    ip_obj = ipaddress.IPv4Address(ip_address)

    # Increment the IP address
    new_ip_obj = ip_obj + 1

    # Convert the result back to a string
    new_ip_address = str(new_ip_obj)

    return new_ip_address

class Bridge:
    def __init__(self, name, ip_address, port):
        self.name = name
        self.ip_address = ip_address
        self.port = port

def parse_bridge_file() -> list[Bridge]:
    bridges = []
    with open(BRIDGE_FILE_PATH, 'r') as file:
        for line in file:
            # Split each line into tokens
            tokens = line.strip().split(',')

            # Check if the line has at least two tokens (name and IP address)
            if len(tokens) >= 3:
                name = tokens[0]
                ip_address = tokens[1]
                port = int(tokens[2])
                bridges.append(Bridge(name,ip_address,port))
    return bridges


def remove_line_from_file(lan_name):

    try:
        # Read the file into a list
        with open(BRIDGE_FILE_PATH, 'r') as file:
            lines = file.readlines()

        # Filter lines that do not match the specified values
        updated_lines = [line for line in lines if lan_name not in line]

        # Write the updated lines back to the file
        with open(BRIDGE_FILE_PATH, 'w') as file:
            file.writelines(updated_lines)
    except:
        print('File does not exist')


def process_data_frame(data):
    source_mac = data[:6]
    dest_mac = data[6:12]
    frame = data[12:]
    return source_mac, dest_mac, frame

def file_write(ip_addrr,PORT, station_name):
    with open(BRIDGE_FILE_PATH, "a") as f:
        f.write(f"{station_name},{ip_addrr},{PORT}\n")