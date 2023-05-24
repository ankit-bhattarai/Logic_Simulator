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
        self.symbol = scanner.list_of_symbols[0]
        self.syntax_error_types = {
            1: "NameError: File should start with keyword 'DEVICES'",
            2: "NameError: semi-colon after the last device should be followed by keyword 'CONNECT'.",
            3: "NameError: semi-colon after the last connection should be followed by keyword 'MONITOR'.",
            4: "NameError: semi-colon after the last monitor should be followed by keyword 'END'.",
            5: "ValueError: There should be at least one device.",
            6: "ValueError: The required number of parameters for a device of the type CLOCK/SWITCH/AND/OR/NAND/NOR is 3. Should also check for incorrect placement or missing punctuations.",
            7: "ValueError: The required number of parameters for a device of the type XOR/DTYPE is 2. Should also check for incorrect placement or missing punctuations.",
            8: "NameError: 1st parameter of a device should be the keyword for that device.",
            9: "TypeError: Device name should be an alphanumeric string (including '_') starting with a lowercase letter.",
            10: "ValueError: Clock speed should be an integer.",
            11: "ValueError: Switch state should be either 0 or 1.",
            12: "ValueError: Number of inputs for an AND/NAND/OR/NOR device should be between 1 and 16.",
            13: "TypeError: Connections should be separated by comma and ended by semi-colon.",
            14: "TypeError: Output pins can only be Q or QBAR.",
            15: "TypeError: 2nd parameter of a connection should be '>'.",
            16: "TypeError: 3rd parameter of a connection must be a device name followed by '.input_pin'.",
            17: "NameError: The input pin should be one of the following: I1, I2,...,I16, DATA, CLK, SET, CLEAR.",
            18: "TypeError: Monitors should be separated by comma and ended by semi-colon."
        }
        self.semantic_error_handler = SemanticErrorHandler(self.names, self.devices, self.network, self.monitors, self.scanner)

    def check_name(self):
        """Check if the current symbol is a name.

        If it is not, display an error message.

        Returns
        -------
        bool
            True if the current symbol is a name, False otherwise.
        """
        if self.symbol.type == "name":
            return True
        else:
            self.display_syntax_error(9, self.symbol)
            return False

    def connection(self, con_list):
        """Parses a single connection, returns errors upon detection

        Creates a list of the current connection.
        Appends this list to the list of connections if no error is detected.
        Appends None to the list of connections if an error is detected.

        Parameters
        ----------
        con_list: list
            list of connections

        Returns
        -------
        bool
            True if no errors detected, return nothing otherwise
        """
        con = []
        if self.check_name():
            con.append(self.names.get_name_string(self.symbol.id))
        else:
            con_list.append(None)
            while self.symbol.type != "comma" and self.symbol.type != "semi-colon":
                self.symbol = self.scanner.get_symbol()
            return
        self.symbol = self.scanner.get_symbol()
        if self.symbol.type == "dot":
            con.append(self.names.get_name_string(self.symbol.id))
            self.symbol = self.scanner.get_symbol()
            if self.symbol.type == "output_pin":
                con.append(self.names.get_name_string(self.symbol.id))
                self.symbol = self.scanner.get_symbol()
            else:
                con_list.append(None)
                self.display_syntax_error(14, self.symbol)
                while self.symbol.type != "comma" and self.symbol.type != "semi-colon":
                    self.symbol = self.scanner.get_symbol()
                return
        if self.symbol.type == "arrow":
            con.append(self.names.get_name_string(self.symbol.id))
        else:
            con_list.append(None)
            self.display_syntax_error(15, self.symbol)
            while self.symbol.type != "comma" and self.symbol.type != "semi-colon":
                self.symbol = self.scanner.get_symbol()
            return
        self.symbol = self.scanner.get_symbol()
        if self.check_name():
            con.append(self.names.get_name_string(self.symbol.id))
        else:
            con_list.append(None)
            while self.symbol.type != "comma" and self.symbol.type != "semi-colon":
                self.symbol = self.scanner.get_symbol()
            return
        self.symbol = self.scanner.get_symbol()
        if self.symbol.type == "dot":
            con.append(self.names.get_name_string(self.symbol.id))
        else:
            con_list.append(None)
            self.display_syntax_error(16, self.symbol)
            while self.symbol.type != "comma" and self.symbol.type != "semi-colon":
                self.symbol = self.scanner.get_symbol()
            return
        self.symbol = self.scanner.get_symbol()
        if self.symbol.type == "input_pin":
            con.append(self.names.get_name_string(self.symbol.id))
            con_list.append(con)
            self.symbol = self.scanner.get_symbol() # 1
            return True
        else:
            con_list.append(None)
            self.display_syntax_error(17, self.symbol)
            return

    def connection_list(self):
        """Parses all connections, returns errors upon detection

        Returns
        -------
        con_list: list
            list of connections
        """
        con_list = []
        self.symbol = self.scanner.get_symbol()
        if self.symbol.type == "semi-colon":  # No connections
            return con_list
        else:
            self.connection(con_list)
        while self.symbol.type == "comma":
            self.symbol = self.scanner.get_symbol()
            self.connection(con_list)
        if self.symbol.type == "semi-colon":
            if None not in con_list:
                return con_list
            else:
                return None
        else:
            self.display_syntax_error(13, self.symbol)
            return

    def monitor(self, mon_list):
        """Parses a monitor, returns errors upon detection

        Creates a list of the current monitor.
        Appends this list to the list of monitors if no error is detected.
        Appends None to the list of monitors if an error is detected.

        Parameters
        ----------
        mon_list: list
            list of monitors

        Returns
        -------
        bool
            True if no errors detected, return nothing otherwise
        """
        mon = []
        if self.check_name():
            mon.append(self.names.get_name_string(self.symbol.id))
        else:
            mon_list.append(None)
            self.symbol = self.scanner.get_symbol()
            while self.symbol.type != "comma" and self.symbol.type != "semi-colon":
                self.symbol = self.scanner.get_symbol()
            return
        self.symbol = self.scanner.get_symbol()
        if self.symbol.type == "comma":
            mon_list.append(mon)
            return True
        elif self.symbol.type == "dot":
            mon.append(self.names.get_name_string(self.symbol.id))
            self.symbol = self.scanner.get_symbol()
            if self.symbol.type == "output_pin":
                mon.append(self.names.get_name_string(self.symbol.id))
                mon_list.append(mon)
                self.symbol = self.scanner.get_symbol()
                return True
            else:
                mon_list.append(None)
                self.display_syntax_error(14, self.symbol)
                self.symbol = self.scanner.get_symbol()
                return

    def monitor_list(self):
        """Parses all monitors, returns errors upon detection
        
        Returns
        -------
        mon_list: list
            list of monitors
        """
        mon_list = []
        self.symbol = self.scanner.get_symbol()
        if self.symbol.type == "semi-colon":  # No monitors
            return mon_list
        else:
            self.monitor(mon_list)
        while self.symbol.type != "comma" and self.symbol.type != "semi-colon":
            self.symbol = self.scanner.get_symbol()
        while self.symbol.type == "comma":
            self.symbol = self.scanner.get_symbol()
            self.monitor(mon_list)
        if self.symbol.type == "semi-colon":
            if None not in mon_list:
                return mon_list
            else:
                return None
        else:
            self.display_syntax_error(18, self.symbol)
            return

    def display_syntax_error(self, error_index, symbol, **kwargs):
        """Display the syntax error.

        Parameters
        ----------
        error_index: int
            Index of the syntax error that occured
        symbol: Symbol
            Symbol associated with the syntax error

        Returns
        -------
        bool
            True if the syntax error is printed, False otherwise.
        """
        error_message = self.syntax_error_types[error_index]
        return self.scanner.print_error(symbol, 0, error_message)
    
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
    
            if self.semantic_error_handler.handle_error(error_code, device):
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
