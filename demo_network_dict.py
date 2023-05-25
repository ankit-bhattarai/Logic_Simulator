"""File contains a demonstration of how to construct a dict of network."""
from names import Names
from scanner import Scanner
from devices import Devices
from network import Network
from monitors import Monitors
from parse import Parser

names_1 = Names()
device_1 = Devices(names_1)
network_1 = Network(names_1, device_1)
monitor_1 = Monitors(names_1, device_1, network_1)
scanner_1 = Scanner("demo_net_dict2.txt", names_1)  # Another file: demo_net_dict2.txt

list_of_symbols_1 = scanner_1.get_list_of_symbols()

print("Contents of demo_net_dict2.txt")
for symbol in list_of_symbols_1:
    id = symbol.id
    name = names_1.get_name_string(id)
    if name == "CONNECT" or name == "MONITOR" or name == "END":
        print()
    print(name, end=" ")
print()

# Check Parser.network_dict()
parser_1 = Parser(names_1, device_1, network_1, monitor_1, scanner_1)
print(parser_1.network_dict())
