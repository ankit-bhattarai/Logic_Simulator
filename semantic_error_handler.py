""" This module contains the SemanticErrorHandler class, which is used to
    handle semantic errors in devices, network or monitors.
    It is used by parser classes to report semantic errors, when they are
    detected.

Classes:
--------
SemanticErrorHandler - class used to handle semantic errors in devices,
                       network or monitors.
"""


class SemanticErrorHandler:
    """ Class used to report semantic errors in devices, network or monitors.
    Parameters:
    -----------
    names: instance of the Names class
        Contains the names of the devices, network and monitors.

    names: instance of the names.Names() class.
    devices: instance of the devices.Devices() class.
    network: instance of the network.Network() class.
    monitors: instance of the monitors.Monitors() class.
    scanner: instance of the scanner.Scanner() class.

    Public methods:
    ---------------
    handle_error(self, unique_error_code, symbols)
        Handles the error code, printing if needed.
    print_error(self, error_type, symbols, **kwargs)
        Prints the semantic error directly.
    print_input_not_connected(self, symbol)
        Prints the input not connected error at the
        end of the connections section of the definition file.
    """

    def __init__(self, names, devices, network, monitors, scanner):
        self.names = names
        self.devices = devices
        self.network = network
        self.monitors = monitors
        self.scanner = scanner

        self.semantic_error_codes = {
            devices.INVALID_QUALIFIER: "Invalid qualifier",  # Shouldn't occur
            devices.NO_QUALIFIER: "No qualifier",  # Shouldn't occur
            devices.BAD_DEVICE: "Bad device",  # Shouldn't occur
            devices.QUALIFIER_PRESENT: "Qualifier present",  # Shouldn't occur
            devices.DEVICE_PRESENT: "Device present",
            network.INPUT_TO_INPUT: "Input to input",
            network.OUTPUT_TO_OUTPUT: "Output to output",
            network.INPUT_CONNECTED: "Input connected",
            network.PORT_ABSENT: "Port absent",
            network.DEVICE_ABSENT: "Device absent",
            monitors.NOT_OUTPUT: "Not output",
            monitors.MONITOR_PRESENT: "Monitor present",  # Warning only
        }

    def get_labelled_symbols(self, symbols):
        """
        Returns the symbols of a connection labelled with a description.
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
        """Returns the name strings of the output and the input.
        Parameters
        ----------
        labelled_symbols: dict
            Dictionary of labelled symbols for a connection
        Returns
        -------
        output: str
            Name of "output" as defined by the user - in the form of "first_device_name.first_port_name"
        input: str
            Name of "input" as defined by the user - in the form of "second_device_name.second_port_name"
        """
        output = self.names.get_name_string(
            labelled_symbols["First device"].id)
        input = self.names.get_name_string(
            labelled_symbols["Second device"].id)

        if labelled_symbols["First port"]:
            output += "." + self.names.get_name_string(
                labelled_symbols["First port"].id
            )
        if labelled_symbols["Second port"]:
            input += "." + self.names.get_name_string(
                labelled_symbols["Second port"].id
            )

        return output, input

    def display_device_present_error(self, device_name_symbol):
        """Prints the device present error.
        Parameters
        ----------
        device_name_symbol: symbol
            Symbol associated with the device present error
        Returns
        -------
        None
        """
        device_name = self.names.get_name_string(device_name_symbol.id)
        error_message = f"Device names are not unique. {device_name} is already the name of a device"
        self.scanner.print_error(device_name_symbol, 0, error_message)

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
        input_name, output_name = self.get_devices_strings(labelled_symbols)

        error_message = f"Input {input_name} is connected to input {output_name}. Connections must be from outputs to inputs."
        self.scanner.print_error(
            labelled_symbols["First device"], 0, error_message)

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
        output_name, input_name = self.get_devices_strings(labelled_symbols)

        error_message = f"Output {output_name} is connected to output {input_name}. Connections must be from outputs to inputs."
        # Since the syntax rules say that an input pin must have a pin
        # This function will thus point at the pin where it is an output, but
        # the system expects an input
        self.scanner.print_error(
            labelled_symbols["Second port"], 0, error_message)

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
        input_name = self.get_devices_strings(labelled_symbols)[1]

        error_message = f"A signal is already connected to input {input_name}. Only one signal must be connected to an input."
        # Pointing at the input pin where the error is
        self.scanner.print_error(
            labelled_symbols["Second port"], 0, error_message)

    def display_port_absent_error(self, symbols):
        """Prints the port absent error.
        Parameters
        ----------
        symbols: List of symbols
            Symbols associated with the port absent error
        Returns
        -------
        None
        """
        labelled_symbols = self.get_labelled_symbols(symbols)

        first_device = self.devices.get_device(
            labelled_symbols["First device"].id)
        second_device = self.devices.get_device(
            labelled_symbols["Second device"].id)
                        
        first_port_id = labelled_symbols['First port'].id if labelled_symbols['First port'] else None
        second_port_id = labelled_symbols["Second port"].id if labelled_symbols["Second port"] else None

        if first_port_id and first_port_id not in first_device.outputs:
            first_port_name = self.names.get_name_string(first_port_id)
            first_device_name = self.names.get_name_string(labelled_symbols["First device"].id)

            error_message = "Port {} is not defined for device {}".format(
                first_port_name, first_device_name)
            self.scanner.print_error(
                labelled_symbols["First port"], 0, error_message)
        
        if second_port_id and second_port_id not in second_device.inputs:
            second_port_name = self.names.get_name_string(second_port_id)
            second_device_name = self.names.get_name_string(labelled_symbols["Second device"].id)

            error_message = "Port {} is not defined for device {}".format(
                second_port_name, second_device_name)
            self.scanner.print_error(
                labelled_symbols["Second port"], 0, error_message)
            

    def display_device_absent_error(self, symbols):
        """Prints the device absent error.
        Parameters
        ----------
        symbols: List of symbols
            Symbols associated with the device absent error
        Returns
        -------
        None
        """
        # Identfy whether a monitor or network error
        if (len(symbols) == 3 and symbols[1].type == "dot") or len(
                symbols) == 1:  # Monitor error
            device_id = symbols[0].id
            device_name = self.names.get_name_string(device_id)
            error_message = "Device {} is not defined".format(device_name)
            self.scanner.print_error(symbols[0], 0, error_message)
        else:  # Network error
            labelled_symbols = self.get_labelled_symbols(symbols)
            first_device_id = labelled_symbols["First device"].id
            second_device_id = labelled_symbols["Second device"].id

            first_device = self.devices.get_device(first_device_id)
            second_device = self.devices.get_device(second_device_id)

            if first_device is None:
                first_device_name = self.names.get_name_string(first_device_id)
                error_message = "Device {} is not defined".format(
                    first_device_name)
                self.scanner.print_error(
                    labelled_symbols["First device"], 0, error_message)

            if second_device is None:
                second_device_name = self.names.get_name_string(
                    second_device_id)
                error_message = "Device {} is not defined".format(
                    second_device_name)
                self.scanner.print_error(
                    labelled_symbols["Second device"], 0, error_message)

    def display_not_output_error(self, symbol):
        """Prints the not output error.
        Parameters
        ----------
        symbol: Symbol
            Symbol associated with the not output error
        Returns
        -------
        None
        """
        error_message = "This is not an output. Only outputs can be monitored."
        self.scanner.print_error(symbol, 0, error_message)

    def display_input_not_connected_error(self, symbol):
        """Prints the input not connected error.
        Parameters
        ----------
        symbol: Symbol
            Symbol associated with last connection
        """
        devices = []

        for device_id in self.devices.find_devices():
            device = self.devices.get_device(device_id)
            for input_id in device.inputs:
                if self.network.get_connected_output(
                        device_id, input_id) is None:
                    devices.append(self.names.get_name_string(device_id))

        error_message = "One or more inputs are left unconnected for the following devices: {}".format(
            devices)
        self.scanner.print_error(symbol, 0, error_message)

    def display_monitor_present_error(self, output_symbol):
        """Prints the monitor present error.
        Parameters
        ----------
        output_symbol: Symbol
            Symbol associated with the monitor present error
        Returns
        -------
        None
        """
        warning_message = "Warning: Monitor exists at this output already."
        self.scanner.print_error(output_symbol, 0, warning_message)

    def print_error(self, error_type, symbols, **kwargs):
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

        Shouldn't occur if syntax for our EBNF has been properly checked -
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
            self.display_port_absent_error(symbols)
        elif error_type == "Device absent":  # Can be triggered by monitors or network
            self.display_device_absent_error(symbols)
        elif error_type == "Not output":
            self.display_not_output_error(symbols[0])
        elif error_type == "Monitor present":
            self.display_monitor_present_error(symbols[0])

    def handle_error(self, unique_error_code, symbols):
        """Prints the error or warning, if present.
        Parameters
        ----------
        unique_error_code: int
            Unique error code associated with the error - supplied by existing modules
        symbols: list of Symbols
            Symbols associated with the error
        Returns
        -------
        True if error is present, False otherwise
        """
        if unique_error_code not in self.semantic_error_codes:
            return False  # No error

        self.print_error(self.semantic_error_codes[unique_error_code], symbols)

        if self.semantic_error_codes[unique_error_code] == 'Monitor present':
            return False  # Warning

        return True  # Error
