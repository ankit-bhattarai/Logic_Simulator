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
        self.symbol = None
        self.num_of_errors = 0
        self.syntax_error_types = {
            1: "NameError: File should start with keyword 'DEVICES'",
            2: "NameError: ';' after the last device should be followed by keyword 'CONNECT'.",
            3: "NameError: ';' after the last connection should be followed by keyword 'MONITOR'.",
            4: "NameError: ';' after the last monitor should be followed by keyword 'END'.",
            5: "ValueError: There should be at least one device.",
            6: "ValueError: The required number of parameters for a device of the type CLOCK/SWITCH/AND/OR/NAND/NOR/RC/SIGGEN is 3. Should also check for incorrect placement of or missing punctuations.",  # MAINTENANCE
            7: "ValueError: The required number of parameters for a device of the type XOR/DTYPE is 2. Should also check for incorrect placement of or missing punctuations.",
            8: "NameError: 1st parameter of a device should be the keyword for that device.",
            9: "TypeError: Device name should be a lowercase alphanumeric string (including '_').",
            10: "ValueError: Clock speed/RC time constant should be a positive integer.",  # MAINTENANCE
            11: "ValueError: Switch state should be either 0 or 1.",
            12: "ValueError: Number of inputs for an AND/NAND/OR/NOR device should be between 1 and 16.",
            13: "TypeError: Connections should be separated by ',' and ended by ';'. Should also check for excessive parameters of a connection.",
            14: "TypeError: Output pins can only be Q or QBAR.",
            15: "TypeError: 2nd parameter of a connection should be '>'.",
            16: "TypeError: 3rd parameter of a connection must be a device name followed by '.input_pin'.",
            17: "NameError: The input pin should be one of the following: I1, I2,...,I16, DATA, CLK, SET, CLEAR.",
            18: "TypeError: Monitors should be separated by ',' and ended by ';'. Should also check for excessive parameters of a monitor.",
            19: "TypeError: Devices should be separated by ',' and ended by ';'. Should also check for excessive parameters of a device.",
            20: "NameError: DEVICES, CONNECT and MONITOR should be followed by ':'.",
            21: "NameError: 'END' should be followed by ';'.",
            22: "RuntimeError: File ends too early. Should check for missing sections.",
            23: "ValueError: Siggen waveform should only consist of 0s and 1s."}  # MAINTENANCE
        self.semantic_error_handler = SemanticErrorHandler(
            self.names, self.devices, self.network, self.monitors, self.scanner)

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

    def check_clock_rc(self, dev, dev_list):
        """Check the parameters of a clock device.

        Update the list of device parameters.
        Append this list to the list of devices if no error is detected.
        Append None to the list of devices if an error is detected.

        Parameters
        ----------
        dev: list
            list of clock device parameters
        dev_list: list
            list of devices

        Returns
        -------
        bool
            True if no errors detected, return nothing otherwise
        """
        dev.append(self.symbol)  # Append symbol
        self.symbol = self.scanner.get_symbol()
        if self.symbol is None:  # *
            dev_list.append(None)
            self.display_syntax_error(22, self.scanner.list_of_symbols[-1])
            return
        if self.symbol.type == "comma" or self.symbol.type == "semi-colon":
            dev_list.append(None)
            self.display_syntax_error(6, self.symbol)
            return
        if self.check_name():
            dev.append(self.symbol)  # Append symbol
        else:
            dev_list.append(None)
            while self.symbol.type != "comma" and self.symbol.type != "semi-colon":
                self.symbol = self.scanner.get_symbol()
                if self.symbol is None:  # *
                    self.display_syntax_error(
                        22, self.scanner.list_of_symbols[-1])
                    return
            return
        self.symbol = self.scanner.get_symbol()
        if self.symbol is None:  # *
            dev_list.append(None)
            self.display_syntax_error(22, self.scanner.list_of_symbols[-1])
            return
        if self.symbol.type == "comma" or self.symbol.type == "semi-colon":
            dev_list.append(None)
            self.display_syntax_error(6, self.symbol)
            return
        if self.symbol.type == "integer":
            dev.append(self.symbol)  # Append symbol
            self.symbol = self.scanner.get_symbol()
            if self.symbol is None:  # *
                dev_list.append(None)
                self.display_syntax_error(22, self.scanner.list_of_symbols[-1])
                return
        else:
            dev_list.append(None)
            self.display_syntax_error(10, self.symbol)
            while self.symbol.type != "comma" and self.symbol.type != "semi-colon":
                self.symbol = self.scanner.get_symbol()
                if self.symbol is None:  # *
                    self.display_syntax_error(
                        22, self.scanner.list_of_symbols[-1])
                    return
            return
        if self.symbol.type == "comma" or self.symbol.type == "semi-colon":
            dev_list.append(dev)
            return True
        else:
            dev_list.append(None)
            self.display_syntax_error(19, self.symbol)
            while self.symbol.type != "comma" and self.symbol.type != "semi-colon" and self.names.get_name_string(self.symbol.id) != "CONNECT":
                self.symbol = self.scanner.get_symbol()
                if self.symbol is None:  # *
                    self.display_syntax_error(
                        22, self.scanner.list_of_symbols[-1])
                    return
            return

    def check_switch(self, dev, dev_list):
        """Check the parameters of a switch device.

        Update the list of device parameters.
        Append this list to the list of devices if no error is detected.
        Append None to the list of devices if an error is detected.

        Parameters
        ----------
        dev: list
            list of switch device parameters
        dev_list: list
            list of devices

        Returns
        -------
        bool
            True if no errors detected, return nothing otherwise
        """
        dev.append(self.symbol)  # Append symbol
        self.symbol = self.scanner.get_symbol()
        if self.symbol is None:  # *
            dev_list.append(None)
            self.display_syntax_error(22, self.scanner.list_of_symbols[-1])
            return
        if self.symbol.type == "comma" or self.symbol.type == "semi-colon":
            dev_list.append(None)
            self.display_syntax_error(6, self.symbol)
            return
        if self.check_name():
            dev.append(self.symbol)  # Append symbol
        else:
            dev_list.append(None)
            while self.symbol.type != "comma" and self.symbol.type != "semi-colon":
                self.symbol = self.scanner.get_symbol()
                if self.symbol is None:  # *
                    self.display_syntax_error(
                        22, self.scanner.list_of_symbols[-1])
                    return
            return
        self.symbol = self.scanner.get_symbol()
        if self.symbol is None:  # *
            dev_list.append(None)
            self.display_syntax_error(22, self.scanner.list_of_symbols[-1])
            return
        if self.symbol.type == "comma" or self.symbol.type == "semi-colon":
            dev_list.append(None)
            self.display_syntax_error(6, self.symbol)
            return
        if self.names.get_name_string(self.symbol.id) in {'0', '1'}:
            dev.append(self.symbol)  # Append symbol
            self.symbol = self.scanner.get_symbol()
            if self.symbol is None:  # *
                dev_list.append(None)
                self.display_syntax_error(22, self.scanner.list_of_symbols[-1])
                return
        else:
            dev_list.append(None)
            self.display_syntax_error(11, self.symbol)
            while self.symbol.type != "comma" and self.symbol.type != "semi-colon":
                self.symbol = self.scanner.get_symbol()
                if self.symbol is None:  # *
                    self.display_syntax_error(
                        22, self.scanner.list_of_symbols[-1])
                    return
            return
        if self.symbol.type == "comma" or self.symbol.type == "semi-colon":
            dev_list.append(dev)
            return True
        else:
            dev_list.append(None)
            self.display_syntax_error(19, self.symbol)
            while self.symbol.type != "comma" and self.symbol.type != "semi-colon" and self.names.get_name_string(self.symbol.id) != "CONNECT":
                self.symbol = self.scanner.get_symbol()
                if self.symbol is None:  # *
                    self.display_syntax_error(
                        22, self.scanner.list_of_symbols[-1])
                    return
            return

    def check_logic_device(self, dev, dev_list):
        """Check the parameters of a logic device.

        Update the list of device parameters.
        Append this list to the list of devices if no error is detected.
        Append None to the list of devices if an error is detected.

        Parameters
        ----------
        dev: list
            list of logic device parameters
        dev_list: list
            list of devices

        Returns
        -------
        bool
            True if no errors detected, return nothing otherwise
        """
        dev.append(self.symbol)  # Append symbol
        self.symbol = self.scanner.get_symbol()
        if self.symbol is None:  # *
            dev_list.append(None)
            self.display_syntax_error(22, self.scanner.list_of_symbols[-1])
            return
        if self.symbol.type == "comma" or self.symbol.type == "semi-colon":
            dev_list.append(None)
            self.display_syntax_error(6, self.symbol)
            return
        if self.check_name():
            dev.append(self.symbol)  # Append symbol
        else:
            dev_list.append(None)
            while self.symbol.type != "comma" and self.symbol.type != "semi-colon":
                self.symbol = self.scanner.get_symbol()
                if self.symbol is None:  # *
                    self.display_syntax_error(
                        22, self.scanner.list_of_symbols[-1])
                    return
            return
        self.symbol = self.scanner.get_symbol()
        if self.symbol is None:  # *
            dev_list.append(None)
            self.display_syntax_error(22, self.scanner.list_of_symbols[-1])
            return
        if self.symbol.type == "comma" or self.symbol.type == "semi-colon":
            dev_list.append(None)
            self.display_syntax_error(6, self.symbol)
            return
        if self.names.get_name_string(self.symbol.id) in {
                f"{i}" for i in range(1, 17)}:
            dev.append(self.symbol)  # Append symbol
            self.symbol = self.scanner.get_symbol()
            if self.symbol is None:  # *
                dev_list.append(None)
                self.display_syntax_error(22, self.scanner.list_of_symbols[-1])
                return
        else:
            dev_list.append(None)
            self.display_syntax_error(12, self.symbol)
            while self.symbol.type != "comma" and self.symbol.type != "semi-colon":
                self.symbol = self.scanner.get_symbol()
                if self.symbol is None:  # *
                    self.display_syntax_error(
                        22, self.scanner.list_of_symbols[-1])
                    return
            return
        if self.symbol.type == "comma" or self.symbol.type == "semi-colon":
            dev_list.append(dev)
            return True
        else:
            dev_list.append(None)
            self.display_syntax_error(19, self.symbol)
            while self.symbol.type != "comma" and self.symbol.type != "semi-colon" and self.names.get_name_string(self.symbol.id) != "CONNECT":
                self.symbol = self.scanner.get_symbol()
                if self.symbol is None:  # *
                    self.display_syntax_error(
                        22, self.scanner.list_of_symbols[-1])
                    return
            return

    def check_dtype_xor(self, dev, dev_list):
        """Check the parameters of a dtype or xor device.

        Update the list of device parameters.
        Append this list to the list of devices if no error is detected.
        Append None to the list of devices if an error is detected.

        Parameters
        ----------
        dev: list
            list of dtypr or xor device parameters
        dev_list: list
            list of devices

        Returns
        -------
        bool
            True if no errors detected, return nothing otherwise
        """
        dev.append(self.symbol)  # Append symbol
        self.symbol = self.scanner.get_symbol()
        if self.symbol is None:  # *
            dev_list.append(None)
            self.display_syntax_error(22, self.scanner.list_of_symbols[-1])
            return
        if self.symbol.type == "comma" or self.symbol.type == "semi-colon":
            dev_list.append(None)
            self.display_syntax_error(7, self.symbol)
            return
        if self.check_name():
            dev.append(self.symbol)  # Append symbol
            self.symbol = self.scanner.get_symbol()
            if self.symbol is None:  # *
                dev_list.append(None)
                self.display_syntax_error(22, self.scanner.list_of_symbols[-1])
                return
        else:
            dev_list.append(None)
            while self.symbol.type != "comma" and self.symbol.type != "semi-colon":
                self.symbol = self.scanner.get_symbol()
                if self.symbol is None:  # *
                    self.display_syntax_error(
                        22, self.scanner.list_of_symbols[-1])
                    return
            return
        if self.symbol.type == "comma" or self.symbol.type == "semi-colon":
            dev_list.append(dev)
            return True
        else:
            dev_list.append(None)
            self.display_syntax_error(19, self.symbol)
            while self.symbol.type != "comma" and self.symbol.type != "semi-colon" and self.names.get_name_string(self.symbol.id) != "CONNECT":
                self.symbol = self.scanner.get_symbol()
                if self.symbol is None:  # *
                    self.display_syntax_error(
                        22, self.scanner.list_of_symbols[-1])
                    return
            return

    def check_siggen(self, dev, dev_list):  # MAINTENANCE
        """Check the parameters of a siggen device.

        Update the list of device parameters.
        Append this list to the list of devices if no error is detected.
        Append None to the list of devices if an error is detected.

        Parameters
        ----------
        dev: list
            list of siggen device parameters
        dev_list: list
            list of devices

        Returns
        -------
        bool
            True if no errors detected, return nothing otherwise
        """
        dev.append(self.symbol)  # Append symbol
        self.symbol = self.scanner.get_symbol()
        if self.symbol is None:
            dev_list.append(None)
            self.display_syntax_error(22, self.scanner.list_of_symbols[-1])
            return
        if self.symbol.type == "comma" or self.symbol.type == "semi-colon":
            dev_list.append(None)
            self.display_syntax_error(6, self.symbol)
            return
        if self.check_name():
            dev.append(self.symbol)  # Append symbol
        else:
            dev_list.append(None)
            while self.symbol.type != "comma" and self.symbol.type != "semi-colon":
                self.symbol = self.scanner.get_symbol()
                if self.symbol is None:
                    self.display_syntax_error(
                        22, self.scanner.list_of_symbols[-1])
                    return
            return
        self.symbol = self.scanner.get_symbol()
        if self.symbol is None:
            dev_list.append(None)
            self.display_syntax_error(22, self.scanner.list_of_symbols[-1])
            return
        if self.symbol.type == "comma" or self.symbol.type == "semi-colon":
            dev_list.append(None)
            self.display_syntax_error(6, self.symbol)
            return
        if self.symbol.is_waveform(self.names.get_name_string(self.symbol.id))[0]:
            dev.append(self.symbol)  # Append symbol
            self.symbol = self.scanner.get_symbol()
            if self.symbol is None:
                dev_list.append(None)
                self.display_syntax_error(22, self.scanner.list_of_symbols[-1])
                return
        else:
            dev_list.append(None)
            self.display_syntax_error(23, self.symbol)
            while self.symbol.type != "comma" and self.symbol.type != "semi-colon":
                self.symbol = self.scanner.get_symbol()
                if self.symbol is None:
                    self.display_syntax_error(
                        22, self.scanner.list_of_symbols[-1])
                    return
            return
        if self.symbol.type == "comma" or self.symbol.type == "semi-colon":
            dev_list.append(dev)
            return True
        else:
            dev_list.append(None)
            self.display_syntax_error(19, self.symbol)
            while self.symbol.type != "comma" and self.symbol.type != "semi-colon" and self.names.get_name_string(self.symbol.id) != "CONNECT":
                self.symbol = self.scanner.get_symbol()
                if self.symbol is None:
                    self.display_syntax_error(
                        22, self.scanner.list_of_symbols[-1])
                    return
            return

    def device(self, dev_list):
        """Parse a single device, return errors upon detection

        Create the list of device parameters.
        Append this list to the list of devices if no error is detected.
        Append None to the list of devices if an error is detected.

        Parameters
        ----------
        dev_list: list
            list of devices

        Returns
        -------
        bool
            True if no errors detected, return nothing otherwise
        """
        dev = []
        if self.names.get_name_string(self.symbol.id) in {'CLOCK', 'RC'}:
            self.check_clock_rc(dev, dev_list)
        elif self.names.get_name_string(self.symbol.id) == 'SWITCH':
            self.check_switch(dev, dev_list)
        elif self.names.get_name_string(self.symbol.id) == 'SIGGEN':
            self.check_siggen(dev, dev_list)  # MAINTENANCE
        elif self.names.get_name_string(self.symbol.id) in {'AND', 'NAND',
                                                            'OR', 'NOR'}:
            self.check_logic_device(dev, dev_list)
        elif self.names.get_name_string(self.symbol.id) in {'XOR', 'DTYPE'}:
            self.check_dtype_xor(dev, dev_list)
        else:
            dev_list.append(None)
            self.display_syntax_error(8, self.symbol)
            while self.symbol.type != "comma" and self.symbol.type != "semi-colon":
                self.symbol = self.scanner.get_symbol()
                if self.symbol is None:  # *
                    self.display_syntax_error(
                        22, self.scanner.list_of_symbols[-1])
                    return
            return

    def device_list(self):
        """Parse all devices, return errors upon detection

        Return a list of devices if no error is detected.
        Return None if an error is detected.

        Returns
        -------
        con_list: list
            list of devices
        """
        dev_list = []
        self.symbol = self.scanner.get_symbol()
        if self.symbol is None:  # *
            self.display_syntax_error(22, self.scanner.list_of_symbols[-1])
            return None
        if self.symbol.type == "semi-colon":  # No devices
            self.display_syntax_error(5, self.symbol)
            self.symbol = self.scanner.get_symbol()  # !!!
            if self.symbol is None:  # *
                self.display_syntax_error(22, self.scanner.list_of_symbols[-1])
            return None
        else:
            self.device(dev_list)
            if self.symbol is None:  # *
                return None
        while self.symbol.type == "comma":
            self.symbol = self.scanner.get_symbol()
            if self.symbol is None:  # *
                self.display_syntax_error(22, self.scanner.list_of_symbols[-1])
                return None
            if self.names.get_name_string(self.symbol.id) == "CONNECT":
                break
            self.device(dev_list)
            if self.symbol is None:  # *
                return None
        if self.symbol.type == "semi-colon":
            self.symbol = self.scanner.get_symbol()
            if self.symbol is None:  # *
                self.display_syntax_error(22, self.scanner.list_of_symbols[-1])
                return None
            if None not in dev_list:
                return dev_list
            else:
                return None
        else:
            if self.names.get_name_string(self.symbol.id) == "CONNECT":
                return None
            self.display_syntax_error(
                19, self.scanner.list_of_symbols[self.scanner.list_of_symbols.index(self.symbol) - 1])
            while self.names.get_name_string(self.symbol.id) != "CONNECT":
                self.symbol = self.scanner.get_symbol()
                if self.symbol is None:  # *
                    self.display_syntax_error(
                        22, self.scanner.list_of_symbols[-1])
                    return None
            return None

    def connection(self, con_list):
        """Parse a single connection, return errors upon detection

        Create a list of the current connection.
        Append this list to the list of connections if no error is detected.
        Append None to the list of connections if an error is detected.

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
            con.append(self.symbol)  # Append symbol
        else:
            con_list.append(None)
            while self.symbol.type != "comma" and self.symbol.type != "semi-colon":
                self.symbol = self.scanner.get_symbol()
                if self.symbol is None:  # *
                    self.display_syntax_error(
                        22, self.scanner.list_of_symbols[-1])
                    return
            return
        self.symbol = self.scanner.get_symbol()
        if self.symbol is None:  # *
            con_list.append(None)
            self.display_syntax_error(22, self.scanner.list_of_symbols[-1])
            return
        if self.symbol.type == "dot":
            con.append(self.symbol)  # Append symbol
            self.symbol = self.scanner.get_symbol()
            if self.symbol is None:  # *
                con_list.append(None)
                self.display_syntax_error(22, self.scanner.list_of_symbols[-1])
                return
            if self.symbol.type == "output_pin":
                con.append(self.symbol)  # Append symbol
                self.symbol = self.scanner.get_symbol()
                if self.symbol is None:  # *
                    con_list.append(None)
                    self.display_syntax_error(
                        22, self.scanner.list_of_symbols[-1])
                    return
            else:
                con_list.append(None)
                self.display_syntax_error(14, self.symbol)
                while self.symbol.type != "comma" and self.symbol.type != "semi-colon":
                    self.symbol = self.scanner.get_symbol()
                    if self.symbol is None:  # *
                        self.display_syntax_error(
                            22, self.scanner.list_of_symbols[-1])
                        return
                return
        if self.symbol.type == "arrow":
            con.append(self.symbol)  # Append symbol
        else:
            con_list.append(None)
            self.display_syntax_error(15, self.symbol)
            while self.symbol.type != "comma" and self.symbol.type != "semi-colon":
                self.symbol = self.scanner.get_symbol()
                if self.symbol is None:  # *
                    self.display_syntax_error(
                        22, self.scanner.list_of_symbols[-1])
                    return
            return
        self.symbol = self.scanner.get_symbol()
        if self.symbol is None:  # *
            con_list.append(None)
            self.display_syntax_error(22, self.scanner.list_of_symbols[-1])
            return
        if self.check_name():
            con.append(self.symbol)  # Append symbol
        else:
            con_list.append(None)
            while self.symbol.type != "comma" and self.symbol.type != "semi-colon":
                self.symbol = self.scanner.get_symbol()
                if self.symbol is None:  # *
                    self.display_syntax_error(
                        22, self.scanner.list_of_symbols[-1])
                    return
            return
        self.symbol = self.scanner.get_symbol()
        if self.symbol is None:  # *
            con_list.append(None)
            self.display_syntax_error(22, self.scanner.list_of_symbols[-1])
            return
        if self.symbol.type == "dot":
            con.append(self.symbol)  # Append symbol
        else:
            con_list.append(None)
            self.display_syntax_error(16, self.symbol)
            while self.symbol.type != "comma" and self.symbol.type != "semi-colon":
                self.symbol = self.scanner.get_symbol()
                if self.symbol is None:  # *
                    self.display_syntax_error(
                        22, self.scanner.list_of_symbols[-1])
                    return
            return
        self.symbol = self.scanner.get_symbol()
        if self.symbol is None:  # *
            con_list.append(None)
            self.display_syntax_error(22, self.scanner.list_of_symbols[-1])
            return
        if self.symbol.type == "input_pin":
            con.append(self.symbol)  # Append symbol
            self.symbol = self.scanner.get_symbol()
            if self.symbol is None:  # *
                con_list.append(None)
                self.display_syntax_error(22, self.scanner.list_of_symbols[-1])
                return
        else:
            con_list.append(None)
            self.display_syntax_error(17, self.symbol)
            self.symbol = self.scanner.get_symbol()  # !!!
            if self.symbol is None:  # *
                self.display_syntax_error(22, self.scanner.list_of_symbols[-1])
            return
        if self.symbol.type == "comma" or self.symbol.type == "semi-colon":
            con_list.append(con)
            return True
        else:
            con_list.append(None)
            self.display_syntax_error(13, self.symbol)
            while self.symbol.type != "comma" and self.symbol.type != "semi-colon" and self.names.get_name_string(self.symbol.id) != "MONITOR":
                self.symbol = self.scanner.get_symbol()
                if self.symbol is None:  # *
                    self.display_syntax_error(
                        22, self.scanner.list_of_symbols[-1])
                    return
            return

    def connection_list(self):
        """Parse all connections, return errors upon detection

        Return a list of all connections if no error is detected.
        Return None otherwise.

        Returns
        -------
        con_list: list
            list of connections
        """
        con_list = []
        self.symbol = self.scanner.get_symbol()
        if self.symbol is None:  # *
            self.display_syntax_error(22, self.scanner.list_of_symbols[-1])
            return None
        if self.symbol.type == "semi-colon":  # No connections
            self.symbol = self.scanner.get_symbol()  # !!!
            if self.symbol is None:  # *
                self.display_syntax_error(22, self.scanner.list_of_symbols[-1])
                return None
            return con_list
        else:
            self.connection(con_list)
            if self.symbol is None:  # *
                return None
        while self.symbol.type == "comma":
            self.symbol = self.scanner.get_symbol()
            if self.symbol is None:  # *
                self.display_syntax_error(22, self.scanner.list_of_symbols[-1])
                return None
            if self.names.get_name_string(self.symbol.id) == "MONITOR":
                break
            self.connection(con_list)
            if self.symbol is None:  # *
                return None
        if self.symbol.type == "semi-colon":
            self.symbol = self.scanner.get_symbol()
            if self.symbol is None:  # *
                self.display_syntax_error(22, self.scanner.list_of_symbols[-1])
                return None
            if None not in con_list:
                return con_list
            else:
                return None
        else:
            if self.names.get_name_string(self.symbol.id) == "MONITOR":
                return None
            self.display_syntax_error(
                13, self.scanner.list_of_symbols[self.scanner.list_of_symbols.index(self.symbol) - 1])
            while self.names.get_name_string(self.symbol.id) != "MONITOR":
                self.symbol = self.scanner.get_symbol()
                if self.symbol is None:  # *
                    self.display_syntax_error(
                        22, self.scanner.list_of_symbols[-1])
                    return None
            return None

    def monitor(self, mon_list):
        """Parse a monitor, return errors upon detection

        Create a list of the current monitor.
        Append this list to the list of monitors if no error is detected.
        Append None to the list of monitors if an error is detected.

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
            mon.append(self.symbol)  # Append symbol
        else:
            mon_list.append(None)
            while self.symbol.type != "comma" and self.symbol.type != "semi-colon":
                self.symbol = self.scanner.get_symbol()
                if self.symbol is None:  # *
                    self.display_syntax_error(
                        22, self.scanner.list_of_symbols[-1])
                    return
            return
        self.symbol = self.scanner.get_symbol()
        if self.symbol is None:  # *
            mon_list.append(None)
            self.display_syntax_error(22, self.scanner.list_of_symbols[-1])
            return
        if self.symbol.type == "comma":
            mon_list.append(mon)
            return True
        elif self.symbol.type == "dot":
            mon.append(self.symbol)  # Append symbol
            self.symbol = self.scanner.get_symbol()
            if self.symbol is None:  # *
                mon_list.append(None)
                self.display_syntax_error(22, self.scanner.list_of_symbols[-1])
                return
            if self.symbol.type == "output_pin":
                mon.append(self.symbol)  # Append symbol
                self.symbol = self.scanner.get_symbol()
                if self.symbol is None:  # *
                    mon_list.append(None)
                    self.display_syntax_error(
                        22, self.scanner.list_of_symbols[-1])
                    return
            else:
                mon_list.append(None)
                self.display_syntax_error(14, self.symbol)
                while self.symbol.type != "comma" and self.symbol.type != "semi-colon":
                    self.symbol = self.scanner.get_symbol()
                    if self.symbol is None:  # *
                        self.display_syntax_error(
                            22, self.scanner.list_of_symbols[-1])
                        return
                return
        if self.symbol.type == "comma" or self.symbol.type == "semi-colon":
            mon_list.append(mon)
            return True
        else:
            mon_list.append(None)
            self.display_syntax_error(18, self.symbol)
            while self.symbol.type != "comma" and self.symbol.type != "semi-colon" and self.names.get_name_string(self.symbol.id) != "END":
                self.symbol = self.scanner.get_symbol()
                if self.symbol is None:  # *
                    self.display_syntax_error(
                        22, self.scanner.list_of_symbols[-1])
                    return
            return

    def monitor_list(self):
        """Parse all monitors, return errors upon detection

        Return a list of all monitors if no error is detected.
        Return None otherwise.

        Returns
        -------
        mon_list: list
            list of monitors
        """
        mon_list = []
        self.symbol = self.scanner.get_symbol()
        if self.symbol is None:  # *
            self.display_syntax_error(22, self.scanner.list_of_symbols[-1])
            return None
        if self.symbol.type == "semi-colon":  # No monitors
            self.symbol = self.scanner.get_symbol()  # !!!
            if self.symbol is None:  # *
                self.display_syntax_error(22, self.scanner.list_of_symbols[-1])
                return None
            return mon_list
        else:
            self.monitor(mon_list)
            if self.symbol is None:  # *
                return None
        while self.symbol.type == "comma":
            self.symbol = self.scanner.get_symbol()
            if self.symbol is None:  # *
                self.display_syntax_error(22, self.scanner.list_of_symbols[-1])
                return None
            if self.names.get_name_string(self.symbol.id) == "END":
                break
            self.monitor(mon_list)
            if self.symbol is None:  # *
                return None
        if self.symbol.type == "semi-colon":
            self.symbol = self.scanner.get_symbol()
            if self.symbol is None:  # *
                self.display_syntax_error(22, self.scanner.list_of_symbols[-1])
                return None
            if None not in mon_list:
                return mon_list
            else:
                return None
        else:
            if self.names.get_name_string(self.symbol.id) == "END":
                return None
            self.display_syntax_error(
                18, self.scanner.list_of_symbols[self.scanner.list_of_symbols.index(self.symbol) - 1])
            while self.names.get_name_string(self.symbol.id) != "END":
                self.symbol = self.scanner.get_symbol()
                if self.symbol is None:  # *
                    self.display_syntax_error(
                        22, self.scanner.list_of_symbols[-1])
                    return None
            return None

    def display_syntax_error(self, error_index, symbol, **kwargs):
        """Display the syntax error.

        Keep track of the number of errors.

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
        name_error = [
            'First character is not a lowercase letter',
            'Specific character is not a letter, digit or underscore',
            'Specific character is not lowercase']
        self.num_of_errors += 1
        error_message = self.syntax_error_types[error_index]
        if error_index == 9:
            name_string = self.names.get_name_string(self.symbol.id)
            index_of_arrow = self.symbol.index_not_name(name_string)[0]
            exact_error_message = name_error[
                self.symbol.index_not_name(name_string)[1] - 1]
            return self.scanner.print_error(
                symbol, index_of_arrow, error_message + exact_error_message)
        elif error_index == 23:
            index_of_arrow = self.symbol.is_waveform(
                self.names.get_name_string(self.symbol.id))[1]
            return self.scanner.print_error(
                symbol, index_of_arrow, error_message)
        return self.scanner.print_error(symbol, 0, error_message)

    def network_dict(self):
        """Verify the syntax of the circuit definition file and return a
        dictionary of symbols describing the network.

        Return False if errors are detected.

        Returns
        -------
        dict: Dictionary of list of list of symbols describing the network.
        """
        network_dict = {}
        self.symbol = self.scanner.get_symbol()
        if self.symbol is None:  # *
            self.display_syntax_error(22, None)
            return False
        # Parse devices
        if self.names.get_name_string(self.symbol.id) != "DEVICES":
            self.display_syntax_error(1, self.symbol)
        self.symbol = self.scanner.get_symbol()
        if self.symbol is None:  # *
            self.display_syntax_error(22, self.scanner.list_of_symbols[-1])
            return False
        if self.symbol.type != "colon":
            self.display_syntax_error(20, self.symbol)
        dev_list = self.device_list()
        if dev_list is not None:
            network_dict["DEVICES"] = dev_list
        if self.symbol is None:  # *
            return False
        # Parse connections
        if self.names.get_name_string(self.symbol.id) != "CONNECT":
            self.display_syntax_error(2, self.symbol)
        self.symbol = self.scanner.get_symbol()
        if self.symbol is None:  # *
            self.display_syntax_error(22, self.scanner.list_of_symbols[-1])
            return False
        if self.symbol.type != "colon":
            self.display_syntax_error(20, self.symbol)
        con_list = self.connection_list()
        if con_list is not None:
            network_dict["CONNECT"] = con_list
        if self.symbol is None:  # *
            return False
        # Parse monitors
        if self.names.get_name_string(self.symbol.id) != "MONITOR":
            self.display_syntax_error(3, self.symbol)
        self.symbol = self.scanner.get_symbol()
        if self.symbol is None:  # *
            self.display_syntax_error(22, self.scanner.list_of_symbols[-1])
            return False
        if self.symbol.type != "colon":
            self.display_syntax_error(20, self.symbol)
        mon_list = self.monitor_list()
        if mon_list is not None:
            network_dict["MONITOR"] = mon_list
        if self.symbol is None:  # *
            return False
        # Parse end
        if self.names.get_name_string(self.symbol.id) != "END":
            self.display_syntax_error(4, self.symbol)
        self.symbol = self.scanner.get_symbol()
        if self.symbol is None:  # *
            self.display_syntax_error(21, self.scanner.list_of_symbols[-1])
            return False
        if self.symbol.type != "semi-colon":
            self.display_syntax_error(21, self.symbol)
        if self.num_of_errors == 0:
            return network_dict
        else:
            return False

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

            # Maintenance - change in type passed to make device
            # Previously, the device property was passed as a string - now int
            device_property = (
                self.names.get_name_string(device[2].id)
                if len(device) == 3
                else None
            )

            # A 'code' is always returned, not all of them are errors
            error_code = self.devices.make_device(device_name, device_type,
                                                  device_property)

            if self.semantic_error_handler.handle_error(error_code, device):
                return False  # Code corresponds to terminal error

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
            # Gather the device and port ids for each connection
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

            error_code = self.network.make_connection(
                first_device, first_port, second_device, second_port)

            # A 'code' is always returned, not all of them are errors
            if self.semantic_error_handler.handle_error(
                    error_code, connection):
                return False  # Code corresponds to terminal error

        if not self.network.check_network():
            self.semantic_error_handler.display_input_not_connected_error(
                connections_list[-1][-1])
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
            port_name = monitor[2].id if len(monitor) == 3 else None
            error_code = self.monitors.make_monitor(device_name, port_name)

            # A 'code' is always returned, not all of them are errors
            if self.semantic_error_handler.handle_error(error_code, monitor):
                return False  # Code corresponds to terminal error

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

        if not self.build_devices(network_dict["DEVICES"]):
            return False  # Semantic error detected in devices
        if not self.build_connections(network_dict["CONNECT"]):
            return False  # Semantic error detected in connections
        if not self.build_monitors(network_dict["MONITOR"]):
            return False  # Semantic error detected in monitors
        return True

    def parse_network(self):
        """Parse the circuit definition file.
        Returns
        -------
        bool: True if the circuit definition file is syntactically and
        semantically correct, False otherwise.
        """
        # Check the syntax of the circuit definition file
        network_dict = self.network_dict()

        if self.num_of_errors == 0 and network_dict:
            # Build the logic network if there are no syntax errors
            build_network = self.build_network(network_dict=network_dict)
        else:  # Print the number of syntax errors detected in the file and exit
            if self.num_of_errors == 1:
                error_message = f"{self.num_of_errors} syntax error detected in the file"
            else:
                error_message = f"{self.num_of_errors} syntax errors detected in the file"
            self.scanner.print_error(None, 0, error_message)
            return False

        # Return the built network if it is semantically correct
        return build_network
