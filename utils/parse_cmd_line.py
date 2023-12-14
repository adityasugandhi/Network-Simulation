import argparse

def parse_station_command_line_args():
    parser = argparse.ArgumentParser(description='Station Script')
    parser.add_argument('interface', type=str, help='Network interface')
    parser.add_argument('routing_table', type=str, help='Routing table file')
    parser.add_argument('hostname_file', type=str, help='Hostname file')

    # Add more arguments if needed

    return parser.parse_args()