from utils.bridge_utils.bridge_init import Bridge

class Bridgeparser:
    def __init__(self):
        self.BRIDGE_FILE_PATH = 'utils/station_utils/bridge.txt'



    def parse_bridge_file(self):
        bridges = []
        with open(self.BRIDGE_FILE_PATH, 'r') as file:
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

    def showbridge(self):
          with open(self.BRIDGE_FILE_PATH, 'r') as file:
            for line in file:
                # Split each line into tokens
                tokens = line.strip().split(',')
                print(tokens)

    def remove_line_from_file(self,lan_name):

        try:
            # Read the file into a list
            with open(self.BRIDGE_FILE_PATH, 'r') as file:
                lines = file.readlines()

            # Filter lines that do not match the specified values
            updated_lines = [line for line in lines if lan_name not in line]

            # Write the updated lines back to the file
            with open(self.BRIDGE_FILE_PATH, 'w') as file:
                file.writelines(updated_lines)
        except:
            print('File does not exist')


    def process_data_frame(data):
        source_mac = data[:6]
        dest_mac = data[6:12]
        frame = data[12:]
        return source_mac, dest_mac, frame
 
    
    
    def file_write(self,ip_addrr,PORT, station_name): 
        with open(self.BRIDGE_FILE_PATH, "a") as f:
            f.write(f"{station_name},{ip_addrr},{PORT}\n")
