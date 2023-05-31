from parse import Parser
from scanner import Symbol
from names import Names
from network import Network
from devices import Devices
from monitors import Monitors

names = Names()

# DEVICES
SWITCH = Symbol("SWITCH", names.lookup(["SWITCH"])[0], 0, 0)
swtich1 = Symbol("switch1", names.lookup(["switch1"])[0], 0, 0)
zero = Symbol("0", names.lookup(["0"])[0], 0, 0)
swtich2 = Symbol("switch2", names.lookup(["switch2"])[0], 0, 0)
AND = Symbol("AND", names.lookup(["AND"])[0], 0, 0)
and1 = Symbol("and1", names.lookup(["and1"])[0], 0, 0)
OR = Symbol("OR", names.lookup(["OR"])[0], 0, 0)
or1 = Symbol("or1", names.lookup(["or1"])[0], 0, 0)
two = Symbol("2", names.lookup(["2"])[0], 0, 0)
NAND = Symbol("NAND", names.lookup(["NAND"])[0], 0, 0)
nand1 = Symbol("nand1", names.lookup(["nand1"])[0], 0, 0)

# CONNECT
arrow = Symbol(">", names.lookup([">"])[0], 0, 0)
I1 = Symbol("I1", names.lookup(["I1"])[0], 0, 0)
dot = Symbol(".", names.lookup(["."])[0], 0, 0)
I2 = Symbol("I2", names.lookup(["I2"])[0], 0, 0)


dict = {"DEVICES": [[SWITCH, swtich1, zero], [SWITCH, swtich2, zero],
                    [AND, and1, two], [OR, or1, two], [NAND, nand1, two]],
        "CONNECTIONS": [[swtich1, arrow, and1, dot, I1],
                    [swtich1, arrow, or1, dot, I1],
                    [swtich2, arrow, and1, dot, I2],
                    [swtich1, arrow, or1, dot, I2],
                    [and1, arrow, nand1, dot, I1],
                    [or1, arrow, nand1, dot, I2]],
        "MONITORS": [[and1], [or1], [nand1]]}

devices = Devices(names=names)
network = Network(names=names, devices=devices)
monitors = Monitors(names=names, devices=devices, network=network)

# Preliminary test case for .build_network() method
parser = Parser(names=names, devices=devices, network=network, monitors=monitors, scanner=None)
parser.build_network(dict)
print(parser.devices.devices_list)