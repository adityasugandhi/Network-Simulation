# Authors as22cq (Aditya Sugandhi) & apf19e (Andrew Franklin)
from utils.station_utils.station_parser import Stationparser
import time
import pandas as pd


class ARPEntry:
    def __init__(self, lan_name, mac_address, entry_time):
        self.lan_name = lan_name
        self.mac_address = mac_address
        self.last_seen = entry_time
        self.timeout = 60



def show_arp_table(arp_table: dict[ARPEntry])-> None:
        ips = []
        mac_addresses = []
        last_seen_times = []

        for ip in arp_table:
            ips.append([ip])
            mac_addresses.append(arp_table[ip].mac_address)
            last_seen_times.append(time.time() - arp_table[ip].last_seen)

        arp_df = pd.DataFrame({
            'IP Address': ip,
            'Mac Addresses': mac_addresses,
            'Last Seen Time': last_seen_times
        })

        print('ARP Table:')
        print(arp_df)


def update_last_seen(self):
     self.last_seen = time.time()

