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
        self.semantic_error_types = {
            devices.INVALID_QUALIFIER: "Invalid qualifier",
            devices.NO_QUALIFIER: "No qualifier",
            devices.BAD_DEVICE: "Bad device",
            devices.QUALIFIER_PRESENT: "Qualifier present",
            devices.DEVICE_PRESENT: "Device present",
            network.INPUT_TO_INPUT: "Input to input",
            network.OUTPUT_TO_OUTPUT: "Output to output",
            network.INPUT_CONNECTED: "Input connected",
            network.PORT_ABSENT: "Port absent",
            network.DEVICE_ABSENT: "Device absent",
            monitors.NOT_OUTPUT: "Not output",
            monitors.MONITOR_PRESENT: "Monitor present",
        }

    def get_labelled_symbols(self, symbols):
        """
        Returns the symbols labelled with description.
        Parameters
        ----------
        symbols: list of symbols asscoiated with the connection
        Returns
        -------
        dict: Dictionary of labelled symbols
        """
        labelled_symbols = {
            "First device": None,
            "First port": None,
            "Second device": None,
            "Second port": None,
        }

        labelled_symbols["First device"] = symbols[0]

        if symbols[1].type == "dot":
            labelled_symbols["First port"] = symbols[2]
            labelled_symbols["Second device"] = symbols[4]
            if symbols[5].type == "dot":
                labelled_symbols["Second port"] = symbols[6]
        else:
            labelled_symbols["Second device"] = symbols[2]
            if symbols[3].type == "dot":
                labelled_symbols["Second port"] = symbols[4]
        return labelled_symbols

    def get_devices_strings(self, labelled_symbols):
        """Returns the device strings.
        Parameters
        ----------
        labelled_symbols: dict
            Dictionary of labelled symbols for a connection
        Returns
        -------
        first_device: str
            String associated for first device + port
        second_device: str
            String associated for second device + port
        """
        first_device = self.names.get_name_string(labelled_symbols["First device"].id)
        second_device = self.names.get_name_string(labelled_symbols["Second device"].id)

        if labelled_symbols["First port"]:
            first_device += "." + self.names.get_name_string(
                labelled_symbols["First port"].id
            )
        if labelled_symbols["Second port"]:
            second_device += "." + self.names.get_name_string(
                labelled_symbols["Second port"].id
            )

        return first_device, second_device

    def display_device_present_error(self, device_name):
        """Prints the device present error.
        Parameters
        ----------
        device_name: symbol
            Symbol associated with the device present error
        Returns
        -------
        None
        """
        self.scanner.print_error(device_name, 0,
                                 "Device names are not unique. {} is already the name of a device".format(self.names.get_name_string(device_name.id))
        )

    def display_input_input_error(self, symbols):
        """Prints the input input error.
        Parameters
        ----------
        symbols: List of symbols
            Symbols associated with the input input error
        Returns
        -------
        None
        """
        labelled_symbols = self.get_labelled_symbols(symbols)
        first_device, second_device = self.get_devices_strings(labelled_symbols)
        self.scanner.print_error(labelled_symbols["First device"], 0, 
                                 "Input {} is connected to input {}".format(first_device, second_device)
                                 + "Connections must be from outputs to inputs.")

    def display_output_output_error(self, symbols):
        """Prints the output output error.
        Parameters
        ----------
        symbols: List of symbols
            Symbols associated with the output output error
        Returns
        -------
        None
        """
        labelled_symbols = self.get_labelled_symbols(symbols)
        first_device, second_device = self.get_devices_strings(labelled_symbols)
        self.scanner.print_error(labelled_symbols["Second device"], 0,
                                 "Output {} is connected to output {}".format(first_device, second_device)
                                 + "Connections must be from outputs to inputs.")

    def display_input_connected_error(self, symbols):
        """Prints the input connected error.
        Parameters
        ----------
        symbols: List of symbols
            Symbols associated with the input connected error
        Returns
        -------
        None
        """
        labelled_symbols = self.get_labelled_symbols(symbols)
        first_device, second_device = self.get_devices_strings(labelled_symbols)

        self.scanner.print_error(labelled_symbols["Second device"], 0,
            "Signal is already connected to input {}".format(second_device)
            + "Only one signal must be connected to an input.")
        

    def display_semantic_error(self, error_type, symbols, **kwargs):
        """Prints the semantic error.
        Parameters
        ----------
        error_type: str
            Desription of the semantic error that occured
        symbol: list of symbols
            Symbols associated with the semantic error
        Returns
        -------
        None
        Shouldn't occur -
        Invalid qualifier, no qualifier, Bad device, Qualifier present
        """
        if error_type == "Device present":
            self.display_device_present_error(symbols[1])
        elif error_type == "Input to input":
            self.display_input_input_error(symbols)
        elif error_type == "Output to output":
            self.display_output_output_error(symbols)
        elif error_type == "Input connected":
            self.display_input_connected_error(symbols)
        elif error_type == "Port absent":
            pass
        elif error_type == "Device absent":
            pass
        elif error_type == "Not output":
            pass
        elif error_type == "Input not connected":
            pass
        elif error_type == "Monitor present":
            pass  # Warning - Not error message

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

            device_error_code = self.devices.make_device(
                device_name, device_type, device_property
            )
            device_error = self.semantic_error_types.get(device_error_code, None)

            if device_error:
                self.display_semantic_error(device_error, device)

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

            connection_error_code = self.network.make_connection(
                first_device, first_port, second_device, second_port
            )
            connection_error = self.semantic_error_types.get(
                connection_error_code, None
            )

            if connection_error:
                self.display_semantic_error(connection_error, connection)
                return False

        if (
            not self.network.check_network()
        ):  # TODO: Consider how to showcase this error to the user
            self.display_semantic_error("Input not connected", None)
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

            monitor_error_code = self.monitors.make_monitor(device_name, port_name)
            monitor_error = self.semantic_error_types.get(monitor_error_code, None)

            if monitor_error:
                self.display_semantic_error(monitor_error, monitor)
                if monitor_error != "Monitor present":
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
