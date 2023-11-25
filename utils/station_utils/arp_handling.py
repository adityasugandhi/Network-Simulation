from utils.station_utils.station_parser import Stationparser
import time


class ARPEntry:
    def __init__(self, ip_address, mac_address, entry_time):
        self.ip_address = ip_address
        self.mac_address = mac_address
        self.entry_timestamp = entry_time
        self.entry_timeout = 60

class ARPTable(Stationparser):
    def __init__(self):
        super().__init__()
        self.arp_entries = []

    def add_arp_entry(self, ip_address, mac_address):
        timestamp = time.time()
        entry = ARPEntry(ip_address, mac_address, timestamp)
        self.arp_entries.append(entry)

    def parse_arp_table(self):
        arp_table = ARPTable()
        with open(self.interface_file, 'r') as file:
            for line in file:
                # Parse the interface file and extract IP and MAC addresses
                tokens = line.strip().split()
                if len(tokens) >= 5:
                    ip_address = tokens[1]
                    mac_address = tokens[3]
                    arp_table.add_arp_entry(ip_address, mac_address)
        return arp_table
    
    def get_mac_address(self, ip_address):
        for entry in self.arp_entries:
            if entry.ip_address == ip_address:
                return entry.mac_address
        return None    
    
    def remove_stale_entries(self):
        # Remove entries that have exceeded the timeout
        current_time = time.time()
        self.arp_entries = [entry for entry in self.arp_entries if (current_time - entry.entry_timestamp) < self.entry_timeout]
