"""
Interface between GUI and devices, names, network, monitors, parser and scanner.
Classes
-------
GuiInterface - interface between GUI and devices, names, network, monitors, parser and scanner.
"""
from names import Names
from devices import Devices
from network import Network
from monitors import Monitors
from scanner import Scanner
from parse import Parser


class GuiInterface():
    """
    parameters
    ----------
    names: instance of the names.Names() class.
    devices: instance of the devices.Devices() class.
    network: instance of the network.Network() class.
    monitors: instance of the monitors.Monitors() class.
    public methods
    --------------
    list_of_switches(self): returns list of switch names (strings)

    list_of_outputs(self): returns list of output names (strings)

    get_switch_state(self, switch_name): returns state of switch (boolean)

    set_switch_state(self, switch_name, switch_state): sets switch state

    get_output_state(self, output_name): returns state of monitor (bool 0 if unmonitored)

    set_output_state(self, output_name, output_state): add or remove monitor

    run_network(self, n_cycles): resets and runs the network for n-cycles

    continue_network(self, n_cycles): continues running the network for n-cycles

    get_signals(self): returns dictionary of all monitered signal states for each monitored output

    update_network(self, definition_file_path): updates network based on the new definition file
    """

    def __init__(self, names, devices, network, monitors, scanner):
        self.names = names
        self.devices = devices
        self.network = network
        self.monitors = monitors
        self.scanner = scanner

    def list_of_switches(self):
        """Returns list of switch names (strings)
        Parameters
        ----------
        No parameters.
        Returns
        -------
        List of switch names (strings)
        """
        switch_type_id = self.names.query("SWITCH")
        switch_ids = self.devices.find_devices(switch_type_id)
        return [self.names.get_name_string(switch_id)
                for switch_id in switch_ids]

    def list_of_outputs(self):
        """Returns list of output names (strings)
        Parameters
        ----------
        No parameters.
        Returns
        -------
        List of output names (strings)
        """
        output_names = [] 

        for device in self.devices.devices_list:
            device_name = self.names.get_name_string(device.device_id)
            for output_port_id in device.outputs.keys():
                if output_port_id:  # if there is an output port - add it to the name
                    output_names.append(
                        device_name + "." + self.names.get_name_string(output_port_id))
                else:
                    output_names.append(device_name)

        return output_names

    def get_switch_state(self, switch_name):
        """Returns state of switch (boolean)
        Parameters
        ----------
        switch_name: name of switch (string)
        Returns
        -------
        State of switch (boolean)
        """
        switch_id = self.names.query(switch_name)
        switch = self.devices.get_device(switch_id)
        return switch.switch_state

    def set_switch_state(self, switch_name, switch_state):
        """Sets switch state
        Parameters
        ----------
        switch_name: name of switch (string)
        switch_state: state of switch (boolean)
        Returns
        -------
        No return value
        """
        switch_id = self.names.query(switch_name)
        switch = self.devices.get_device(switch_id)
        switch.switch_state = switch_state

    def get_output_state(self, output_name):
        """Returns state of monitor (bool 0 if unmonitored)
        Parameters
        ----------
        output_name: name of output (string)
        Returns
        -------
        State of monitor (bool 0 if unmonitored)
        """
        split_name = output_name.split(".")
        device_id = self.names.query(split_name[0])
        port_id = self.names.query(
            split_name[1]) if len(split_name) == 2 else None
        # if the output is in the monitor dictionary, return True 
        if (device_id, port_id) in self.monitors.monitors_dictionary:
            return True
        return False

    def set_output_state(self, output_name, output_state):
        """Add or remove monitor
        Parameters
        ----------
        output_name: name of output (string)
        output_state: state of monitor (boolean)
        Returns
        -------
        No return value
        """
        split_name = output_name.split(".")
        device_id = self.names.query(split_name[0])
        port_id = self.names.query(
            split_name[1]) if len(split_name) == 2 else None
        if output_state: # Add monitor
            self.monitors.make_monitor(device_id, port_id)
        else: # Remove monitor
            self.monitors.remove_monitor(device_id, port_id)

    def run_network(self, n_cycles):
        """Resets and runs the network for n-cycles
        Parameters
        ----------
        n_cycles: number of cycles to run (int)
        Returns
        -------
        Return True if network is running, "Network oscillating!" if network is oscillating
        """
        self.devices.cold_startup()
        self.monitors.reset_monitors()
        for i in range(n_cycles):
            # Important check to see if network is oscillating
            if not self.network.execute_network():
                return "Network oscillating!"
            self.monitors.record_signals()
        return True

    def continue_network(self, n_cycles):
        """Continues running the network for n-cycles
        Parameters
        ----------
        n_cycles: number of cycles to run (int)
        Returns
        -------
        Return True if network is running, "Network oscillating!" if network is oscillating
        """
        for i in range(n_cycles):
            if not self.network.execute_network():
                # Important check to see if network is oscillating
                return "Network oscillating!"
            self.monitors.record_signals()
        return True

    def get_signals(self):
        """Returns dictionary of all monitered signal states for each monitored output
        Parameters
        ----------
        No parameters.
        Returns
        -------
        Dictionary of all monitered signal states for each monitored output
        """
        max_length = -1
        signals_dictionary = {} # Output signal name (str): list of signal values (bool)

        for key, value in self.monitors.monitors_dictionary.items():
            device_id, port_id = key
            output_name_string = self.names.get_name_string(device_id)
            if port_id:
                output_name_string += "." + self.names.get_name_string(port_id)

            signals_dictionary[output_name_string] = value
            max_length = max(max_length, len(value))
        
        # Pad the signals with None values to make them all the same length
        # (signal values are only recorded when they are monitored)
        for key, value in signals_dictionary.items():
            signals_dictionary[key] = [None] * \
                (max_length - len(value)) + value

        return signals_dictionary

    def update_network(self, definition_file_path):
        """Updates network based on the new definition file.

        Method tries to build the network with the new definition file.
        If the network is built successfully, the current network is updated.
        Otherwise, the current network is left unchanged.

        Parameters
        ----------
        definition_file_path: string
            path to the new definition file

        Returns
        -------
        success: bool
            True if the network is updated successfully, False otherwise
        error_messages: string
            Any error or warning messages that occurred during parsing
        """
        # Create new instances of all the classes - for the new network
        new_names = Names()
        new_devices = Devices(new_names)
        new_network = Network(new_names, new_devices)
        new_monitors = Monitors(new_names, new_devices, new_network)
        new_scanner = Scanner(definition_file_path, new_names)
        new_scanner.print_to_gui = True
        new_parser = Parser(new_names, new_devices,
                            new_network, new_monitors, new_scanner)
        if new_parser.parse_network():
            # If able to parse the new network and build it, update the network
            self.names = new_names
            self.devices = new_devices
            self.network = new_network
            self.monitors = new_monitors
            self.scanner = new_scanner
            passed = True
        else:  # Don't update the network if the new definition file is invalid
            passed = False 
        # Get any error messages from the scanner - for printing to GUI
        error_messages = new_scanner.get_error_messages()
        return passed, error_messages
