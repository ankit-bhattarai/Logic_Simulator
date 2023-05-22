"""Parse the definition file and build the logic network.

Used in the Logic Simulator project to analyse the syntactic and semantic
correctness of the symbols received from the scanner and then builds the
logic network.

Classes
-------
Parser - parses the definition file and builds the logic network.
"""


class Parser:

    """Parse the definition file and build the logic network.

    The parser deals with error handling. It analyses the syntactic and
    semantic correctness of the symbols it receives from the scanner, and
    then builds the logic network. If there are errors in the definition file,
    the parser detects this and tries to recover from it, giving helpful
    error messages.

    Parameters
    ----------
    names: instance of the names.Names() class.
    devices: instance of the devices.Devices() class.
    network: instance of the network.Network() class.
    monitors: instance of the monitors.Monitors() class.
    scanner: instance of the scanner.Scanner() class.

    Public methods
    --------------
    parse_network(self): Parses the circuit definition file.
    """

    def __init__(self, names, devices, network, monitors, scanner):
        """Initialise constants."""
        self.names = names
        self.devices = devices
        self.network = network
        self.monitors = monitors
        self.scanner = scanner
        self.semantic_error_types = {devices.INVALID_QUALIFIER: "Invalid qualifier",
                                     devices.NO_QUALIFIER: "No qualifier",
                                     devices.BAD_DEVICE: "Bad device",
                                     devices.QUALIFIER_PRESENT: "Qualifier present",
                                     devices.DEVICE_PRESENT: "Device present", 
                                     network.INVALID_DEVICE: "Invalid device",
                                     network.INVALID_PORT: "Invalid port",
                                     network.PORT_PRESENT: "Port present",
                                     network.DEVICE_PRESENT: "Device present",
                                     network.SAME_DEVICE: "Same device",
                                     network.SAME_PORT: "Same port",
                                     network.INVALID_CONNECTION: "Invalid connection",
                                     monitors.NOT_OUTPUT: "Not output",
                                     monitors.MONITOR_PRESENT: "Monitor present"}

    def display_semantic_error(self, error_type, symbol, **kwargs):
        """Display the semantic error."""
        return 
    
    def display_syntax_error(self, error_type, symbol, **kwargs):
        """Display the syntax error."""
        return 
    
    def network_dict(self):
        """Verify the syntax of the circuit definition file and returns a 
        dictionary of symbols describing the network."""
        # For now just return True, so that userint and gui can run in the
        # skeleton code. When complete, should return False when there are
        # errors in the circuit definition file.
        return True
    
    def build_devices(self, devices_list):
        for device in devices_list: 
            device_type = device[0].id
            device_name = device[1].id
            device_property = device[2].id if len(device)==3 else None

            device_error_code = self.devices.make_device(device_type, 
                                                        device_name, 
                                                        device_property)
            device_error = self.semantic_error_types.get(device_error_code, None)
            
            if device_error:
                self.display_semantic_error(device_error, device)
                return False
        return True     
    
    def build_connections(self, connections_list):
        for connection in connections_list:
            first_device = connection[0].id
            first_port = second_port = None

            if connection[1].type == "dot":
                first_port = connection[2].id
                second_device = connection[4].id
                if connection[5].type == "dot":
                    second_port = connection[6].id
            else:
                second_device = connection[2].id
                if connection[3].type == "dot":
                    second_port = connection[4].id
                
            connection_error_code = self.network.make_connection(first_device, first_port, 
                                                                 second_device, second_port)  
            connection_error = self.semantic_error_types.get(connection_error_code, None)
            if connection_error:
                self.display_semantic_error(connection_error, connection)
                return False
        return True
    
    def build_monitors(self, monitors_list):    
        for monitor in monitors_list:
            device_name = monitor[0].id
            port_name = monitor[3].id if len(monitor)==3 else None

            monitor_error_code = self.monitors.make_monitor(device_name, port_name)
            monitor_error = self.semantic_error_types.get(monitor_error_code, None)
            
            if monitor_error:
                self.display_semantic_error(monitor_error, monitor)
                return False   
        return True  
    
    def build_network(self, network_dict):
        """Build the logic network."""
        # For now just return True, so that userint and gui can run in the
        # skeleton code. When complete, should return False when there are
        # errors in the circuit definition file.
        # Semantic error identification and handling
        if not self.build_devices(network_dict["DEVICES"]):
            return False
        if not self.build_connections(network_dict["CONNECTIONS"]):
            return False
        if not self.build_monitors(network_dict["MONITORS"]):
            return False
        return True 

    def parse_network(self):
        """Parse the circuit definition file."""
        # For now just return True, so that userint and gui can run in the
        # skeleton code. When complete, should return False when there are
        # errors in the circuit definition file.
        network_dict = self.network_dict()
        if network_dict:
            build_network = self.build_network()
        else:
            return False

        return build_network