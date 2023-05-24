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
    """
    def __init__(self, names, devices, network, monitors, scanner):
        self.names = names
        self.devices = devices
        self.network = network
        self.monitors = monitors
        self.scanner = scanner

        self.semantic_error_codes = {
            devices.INVALID_QUALIFIER: "Invalid qualifier", # Shouldn't occur   
            devices.NO_QUALIFIER: "No qualifier", # Shouldn't occur
            devices.BAD_DEVICE: "Bad device", # Shouldn't occur
            devices.QUALIFIER_PRESENT: "Qualifier present", # Shouldn't occur
            devices.DEVICE_PRESENT: "Device present", 
            network.INPUT_TO_INPUT: "Input to input",
            network.OUTPUT_TO_OUTPUT: "Output to output",
            network.INPUT_CONNECTED: "Input connected",
            network.PORT_ABSENT: "Port absent",
            network.DEVICE_ABSENT: "Device absent",
            monitors.NOT_OUTPUT: "Not output",
            monitors.MONITOR_PRESENT: "Monitor present", # Warning only
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
        self.scanner.print_error(device_name_symbol, 0, 
                                 "Device names are not unique. {} is already the name of a device".format(self.names.get_name_string(device_name_symbol.id)))

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
        #TODO: Decide whether look back to print first device connected as well
        
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
        first_device, second_device = self.get_devices_strings(labelled_symbols)
        # TODO: Logic to print out this error meaningfully

    
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
        if (len(symbols) == 3 and symbols[1].type == "dot") or len(symbols) == 1:
            # Monitor error
            self.scanner.print_error(symbols[0], 0, "Device {} is not defined".format(self.names.get_name_string(symbols[0].id)))
        else:
            # TODO: Network error logic here
            pass

    def display_not_output_error(self, symbols):
        """Prints the not output error.
        Parameters
        ----------
        symbols: List of symbols
            Symbols associated with the not output error
        Returns
        -------
        None
        """
        self.scanner.print_error(symbols[0], 0,
                                 "This not an output. Only outputs can be monitored.")
    
    def display_input_not_connected_error(self, symbols):
        """Prints the input not connected error.
        Parameters
        ----------
        symbols: List of symbols
            Symbols associated with the input not connected error
        Returns
        -------
        None
        """
        # TODO: Logic to print out this error meaningfully - search through network

    
    def display_monitor_present_error(self, symbols):
        """Prints the monitor present error.
        Parameters
        ----------
        symbols: List of symbols
            Symbols associated with the monitor present error
        Returns
        -------
        None
        """
        self.scanner.print_error(symbols[0], 0,
                                 "Warning: Monitor exists at this output already.")

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
            self.display_port_absent_error(symbols)
        elif error_type == "Device absent": # Can be triggered by monitors or network
            self.display_device_absent_error(symbols)
        elif error_type == "Not output":
            self.display_not_output_error(symbols)
        elif error_type == "Input not connected":
            self.display_input_not_connected_error(symbols)
        elif error_type == "Monitor present":
            self.display_monitor_present_error(symbols)
    
    def handle_error(self, unique_error_code, symbols):
        """Prints the error or warning, if present.
        Parameters
        ----------
        unique_error_code: int
            Unique error code associated with the error
        symbol: list of symbols
            Symbols associated with the error
        Returns
        -------
        True if error is present, False otherwise
        """
        if unique_error_code not in self.semantic_error_types:
            return False # No error
        else:
            self.print_error(self.semantic_error_types[unique_error_code], symbols)
            if self.semantic_error_types[unique_error_code] == 'Monitor present':
                return False # Warning
        return True # Error Present - Not warning
