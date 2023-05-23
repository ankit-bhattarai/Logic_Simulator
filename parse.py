"""Parse the definition file and build the logic network.

Used in the Logic Simulator project to analyse the syntactic and semantic
correctness of the symbols received from the scanner and then builds the
logic network.

Classes
-------
Parser - parses the definition file and builds the logic network.
"""
from semantic_error_handler import SemanticErrorHandler

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
    semantic_error_handler: instance of the SemanticErrorHandler() class.

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
        self.semantic_error_handler = SemanticErrorHandler(names, devices, network, monitors, scanner)

    def display_syntax_error(self, error_type, symbol, **kwargs):
        """Display the syntax error.
        Parameters
        ----------
        error_type: str
            Description of the syntax error that occured
        symbol: Symbol
            Symbol associated with the syntax error
        Returns
        -------
        None"""
        return

    def network_dict(self):
        """Verify the syntax of the circuit definition file and returns a
        dictionary of symbols describing the network.
        Returns
        -------
        dict: Dictionary of list of list of symbols describing the network."""
        # For now just return True, so that userint and gui can run in the
        # skeleton code. When complete, should return False when there are
        # errors in the circuit definition file.
        return True

    def build_devices(self, devices_list):
        """Build the devices.
        Parameters:
        -----------
        devices_list: list of list of symbols
            List of list of symbols describing the devices.
        Returns
        -------
        bool: True if the devices are semantically correct,
        False otherwise."""
        for device in devices_list:
            device_type = device[0].id
            device_name = device[1].id
            device_property = (
                    int(self.names.get_name_string(device[2].id))
                    if len(device) == 3
                    else None
            )
            error_code = self.devices.make_device(device_name, device_type,
                                                  device_property)
    
            if self.semantic_error_handler.display_error(error_code, device):
                return False

        return True

    def build_connections(self, connections_list):
        """Build the connections.
        Parameters:
        -----------
        connections_list: list of list of symbols
            List of list of symbols describing the connections.
        Returns
        -------
        bool: True if the connections are semantically correct,
        False otherwise."""
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

            error_code = self.network.make_connection(first_device, first_port, 
                                                      second_device, second_port)
            
            if self.semantic_error_handler.handle_error(error_code, connection):
                return False

        if not self.network.check_network():
            self.semantic_error_handler.print_error("Input not connected", [])
            return False
        
        return True

    def build_monitors(self, monitors_list):
        """Build the monitors.
        Parameters:
        -----------
        monitors_list: list of list of symbols
            List of list of symbols describing the monitors.
        Returns
        -------
        bool: True if the monitors are semantically correct,
        False otherwise."""

        for monitor in monitors_list:
            device_name = monitor[0].id
            port_name = monitor[3].id if len(monitor) == 3 else None
            error_code = self.monitors.make_monitor(device_name, port_name)

            if self.semantic_error_handler.handle_error(error_code, monitor):
                return False

        return True

    def build_network(self, network_dict):
        """Build the logic network.
        Parameters:
        -----------
        network_dict: dict
            Dictionary of list of list ofsymbols describing the network.
            (Keys: DEVICES, CONNECTIONS, MONITORS)
        Returns
        -------
        bool: True if the circuit definition file is semantically correct,
        False otherwise.
        """

        devices_success = self.build_devices(network_dict["DEVICES"])
        connections_success = self.build_connections(network_dict["CONNECTIONS"])
        monitors_success = self.build_monitors(network_dict["MONITORS"])
        if all([devices_success, connections_success, monitors_success]):
            return True
        return False

    def parse_network(self):
        """Parse the circuit definition file.
        Returns
        -------
        bool: True if the circuit definition file is syntactically and
        semantically correct, False otherwise.
        """
        network_dict = self.network_dict()
        if network_dict:
            build_network = self.build_network(network_dict=network_dict)
        else:
            return False

        return build_network
