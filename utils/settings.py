import os

interface_file = os.path.abspath('./project/ifaces/ifaces.a')
routingtable_file = os.path.abspath('./project/rtables/rtable.a')
host_file = os.path.abspath('./project/hosts')
    


class ActiveBridges:
    def __init__(self, manager) -> None:
        self.active_bridges = manager.list()

    def add_bridge(self,name,ip_address, port):
        current_names = [bridge['Name'] for bridge in self.active_bridges]
        if name not in current_names:
            self.active_bridges.append({
                'Name': name,
                'IP Address': ip_address,
                'Port': port
            })

    def get_current_bridges(self):
        return [bridge['Name'] for bridge in self.active_bridges]
    

