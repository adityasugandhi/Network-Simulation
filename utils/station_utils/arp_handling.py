# Authors as22cq (Aditya Sugandhi) & apf19e (Andrew Franklin)
from utils.station_utils.station_parser import Stationparser
import time


class ARPEntry:
    def __init__(self, lan_name, mac_address, entry_time, default=False):
        self.lan_name = lan_name
        self.mac_address = mac_address
        self.last_seen = entry_time
        self.timeout = 60
        self.default = default
    def update_last_seen(self):
     self.last_seen = time.time()



def show_arp_table(arp_table: dict[ARPEntry])-> None:
            ips = []
            mac_addresses = []
            last_seen_times = []

            for ip in arp_table:
                ips.append(ip)
                mac_addresses.append(arp_table[ip].mac_address)
                
                last_seen_times.append(time.time() - arp_table[ip].last_seen)

               
            output = "ARP Table:\n"
            output += "{:<15} {:<15} {:<15}\n".format("IP Addresses", "MAC Addresses", "Last Seen Time")

            for i in range(len(ips)):
                output += "{:<15} {:<15} {:<15}\n".format(ips[i], mac_addresses[i], last_seen_times[i])

            return output


    

