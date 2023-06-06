"""Test the semantic_error_handling module."""
import pytest
from unittest.mock import MagicMock
from names import Names
from devices import Devices
from network import Network
from monitors import Monitors
from scanner import Scanner, Symbol
from parse import Parser
from semantic_error_handler import SemanticErrorHandler


@pytest.fixture
def new_names():
    """Return a new names instance."""
    return Names()


@pytest.fixture
def new_devices(new_names):
    """Return a new devices instance."""
    return Devices(new_names)


@pytest.fixture
def new_network(new_names, new_devices):
    """Return a new network instance."""
    return Network(new_names, new_devices)


@pytest.fixture
def new_monitors(new_names, new_devices, new_network):
    """Return a new monitors instance."""
    return Monitors(new_names, new_devices, new_network)


@pytest.fixture
def new_scanner(new_names):
    """Return a new scanner instance."""
    scanner = Scanner(
        "test_parse_files/file_for_test_semantic_error_handling.txt",
        new_names)
    scanner.print_error = MagicMock()
    return scanner


@pytest.fixture
def new_parser(new_names, new_devices, new_network, new_monitors, new_scanner):
    """Return a new parser instance."""
    parser = Parser(new_names, new_devices, new_network,
                    new_monitors, new_scanner)
    parser.parse_network()  # Important to build the network
    return parser


@pytest.fixture
def new_semantic_error_handler(new_names, new_devices, new_network,
                               new_monitors, new_scanner, new_parser):
    """Return a new semantic error handler instance."""
    return SemanticErrorHandler(new_names, new_devices, new_network,
                                new_monitors, new_scanner)


@pytest.fixture
def switch1():
    """Return a switch symbol."""
    return Symbol('switch1', 18, 1, 17)


@pytest.fixture
def arrow():
    """Return an arrow symbol."""
    return Symbol('>', 30, 4, 18)


@pytest.fixture
def dtype1():
    """Return a dtype symbol."""
    return Symbol('dtype1', 25, 1, 68)


@pytest.fixture
def dot():
    """Return a dot symbol."""
    return Symbol('.', 31, 4, 26)


@pytest.fixture
def data_pin():
    """Return a data pin symbol."""
    return Symbol('DATA', 13, 4, 27)


@pytest.fixture
def qbar_pin():
    """Return a qbar pin symbol."""
    return Symbol('QBAR', 15, 6, 8)


@pytest.fixture
def xor1():
    """Return an xor symbol."""
    return Symbol('xor1', 27, 5, 35)


@pytest.fixture
def nor1():
    """Return a nor symbol."""
    return Symbol('nor1', 26, 2, 14)


@pytest.fixture
def I1_pin():
    """Return an I1 pin symbol."""
    return Symbol('I1', 32, 4, 70)


@pytest.fixture
def I3_pin(new_names):
    """Return an I3 pin symbol."""
    id = new_names.lookup(['I3'])[0]
    return Symbol('I3', id, 99, 99)


@pytest.fixture
def clear_pin():
    return Symbol('CLEAR', 12, 5, 18)


@pytest.fixture
def and1(new_names):
    """Return an and symbol."""
    id = new_names.lookup(['and1'])[0]
    return Symbol('and1', id, 100, 100)


@pytest.fixture
def list_of_symbols_1(switch1, arrow, dtype1, dot, data_pin):
    """Return the first list of symbols."""
    return [switch1, arrow, dtype1, dot, data_pin]


@pytest.fixture
def list_of_symbols_2(dtype1, dot, qbar_pin, arrow, xor1, I1_pin):
    """Return the second list of symbols."""
    return [dtype1, dot, qbar_pin, arrow, xor1, dot, I1_pin]


@pytest.fixture
def first_labelled_dictionary(switch1, dtype1, data_pin):
    """Return the first labelled dictionary."""
    return {"First device": switch1, "First port": None,
            "Second device": dtype1, "Second port": data_pin}


@pytest.fixture
def second_labelled_dictionary(dtype1, qbar_pin, xor1, I1_pin):
    """Return the second labelled dictionary."""
    return {"First device": dtype1, "First port": qbar_pin,
            "Second device": xor1, "Second port": I1_pin}


@pytest.fixture
def input_input_error_list(nor1, dot, I1_pin, arrow, xor1):
    """Return a list of symbols which will have an input-input error."""
    return [nor1, dot, I1_pin, arrow, xor1, dot, I1_pin]


def test_get_labelled_symbols(new_semantic_error_handler, list_of_symbols_1, list_of_symbols_2,
                              first_labelled_dictionary, second_labelled_dictionary):
    """Test the get_labelled_symbols method."""
    # There are only two possible inputs for the get_labelled_symbols method.
    # One of them specifies a pin on the output device, and the other one
    # doesn't. Both of them are tested here.
    error_handler = new_semantic_error_handler
    assert error_handler.get_labelled_symbols(
        list_of_symbols_1) == first_labelled_dictionary
    assert error_handler.get_labelled_symbols(
        list_of_symbols_2) == second_labelled_dictionary


@pytest.fixture
def devices_string_first_labelled_dictionary():
    """Return the string names from the first labelled dictionary."""
    output = "switch1"
    input = "dtype1.DATA"
    return output, input


@pytest.fixture
def devices_string_second_labelled_dictionary():
    """Return the string names from the second labelled dictionary."""
    output = "dtype1.QBAR"
    input = "xor1.I1"
    return output, input


def test_get_devices_strings(devices_string_first_labelled_dictionary,
                             first_labelled_dictionary,
                             second_labelled_dictionary,
                             devices_string_second_labelled_dictionary,
                             new_semantic_error_handler):
    """Test the get_devices_string method."""
    assert new_semantic_error_handler.get_devices_strings(first_labelled_dictionary) == \
        devices_string_first_labelled_dictionary
    assert new_semantic_error_handler.get_devices_strings(second_labelled_dictionary) == \
        devices_string_second_labelled_dictionary


def test_display_device_present_error(new_semantic_error_handler, switch1,
                                      new_scanner):
    """Test the display_device_present_error method.

    The test file is clean and doesn't contain any duplicate device
    names, this method just checks that semantic_error_handler's
    display_device_present_error method calls scanner's print_error
    with the correct arguments properly as that is all which the method does. 
    switch1 is the example device name which it is tested with.

    The scanner's print_error method is mocked to check that it is called with
    the correct arguments. As the scanner method is already tested, it prevents
    the same test from being repeated here.
    """
    new_semantic_error_handler.display_device_present_error(switch1)
    new_scanner.print_error.assert_called_with(
        switch1, 0,
        "Device names are not unique. switch1 is already the name of a device")
    assert new_scanner.print_error.call_count == 1


def test_display_input_input_error(new_semantic_error_handler,
                                   input_input_error_list, new_scanner, nor1):
    """Test the display_input_input_error method."""
    new_semantic_error_handler.display_input_input_error(
        input_input_error_list)
    new_scanner.print_error.assert_called_with(nor1, 0,
                                               "Input nor1.I1 is connected to input xor1.I1. Connections must be from outputs to inputs.")
    assert new_scanner.print_error.call_count == 1


@pytest.fixture
def list_output_output_error(xor1, arrow, dtype1, dot, qbar_pin):
    """Return a list of symbols which will have an output-output error."""
    return [xor1, arrow, dtype1, dot, qbar_pin]


def test_output_output_error(new_semantic_error_handler, list_output_output_error,
                             new_scanner, qbar_pin):
    """Test the display_output_output_error method."""
    new_semantic_error_handler.display_output_output_error(
        list_output_output_error)
    # The method is supposed to point at the second device where the system
    # expects to be an input, but is actually an output.
    new_scanner.print_error.assert_called_with(qbar_pin, 0,
                                               "Output xor1 is connected to output dtype1.QBAR. Connections must be from outputs to inputs.")
    assert new_scanner.print_error.call_count == 1


@pytest.fixture
def list_of_symbols_input_connected_error(switch1, arrow, dtype1, dot, clear_pin):
    """Return a list of symbols which will have an input connected error."""
    return [switch1, arrow, dtype1, dot, clear_pin]


def test_display_input_connected_error(new_semantic_error_handler,
                                       list_of_symbols_input_connected_error,
                                       new_scanner, clear_pin):
    """Test the display_input_connected_error method."""
    new_semantic_error_handler.display_input_connected_error(
        list_of_symbols_input_connected_error)
    new_scanner.print_error.assert_called_with(clear_pin, 0,
                                               "Signal switch2 is already connected to the input pin dtype1.CLEAR. Only one signal must be connected to an input.")
    assert new_scanner.print_error.call_count == 1


@pytest.fixture
def list_display_port_absent_error_output(switch1, arrow, nor1, dot, I3_pin):
    """Return a list of symbols which will have a port absent error on the output."""
    return [switch1, arrow, nor1, dot, I3_pin]


@pytest.fixture
def list_display_port_absent_error_input(nor1, dot, qbar_pin, arrow, xor1, I1_pin):
    """Return a list of symbols which will have a port absent error on the input."""
    return [nor1, dot, qbar_pin, arrow, xor1, dot, I1_pin]


def test_display_port_absent_error(new_semantic_error_handler, list_display_port_absent_error_output,
                                   list_display_port_absent_error_input, new_scanner, I3_pin, qbar_pin):
    """Test the display_port_absent_error method."""
    new_semantic_error_handler.display_port_absent_error(
        list_display_port_absent_error_input)
    new_scanner.print_error.assert_called_with(qbar_pin, 0,
                                               "Port QBAR is not defined for device nor1")
    assert new_scanner.print_error.call_count == 1
    new_semantic_error_handler.display_port_absent_error(
        list_display_port_absent_error_output)
    new_scanner.print_error.assert_called_with(I3_pin, 0,
                                               "Port I3 is not defined for device nor1")
    assert new_scanner.print_error.call_count == 2


@pytest.fixture
def list_display_device_absent_error_monitor_2(and1, dot, I1_pin):
    """Return a list of symbols which will have a device absent error on the monitor."""
    return [and1, dot, I1_pin]


@pytest.fixture
def list_display_device_absent_error_connection_input(and1, arrow, xor1, dot,
                                                      I1_pin):
    """Return a list of symbols which have a device absent error on the connection from the input."""
    return [and1, arrow, xor1, dot, I1_pin]


@pytest.fixture
def list_display_device_absent_error_connection_output(xor1, arrow, and1, dot, I1_pin):
    """Return a list of symbols which will have a device absent error on the connection from the output."""
    return [xor1, arrow, and1, dot, I1_pin]


@pytest.fixture
def list_display_device_absent_error_connection_no_call(dtype1, dot, qbar_pin,
                                                        arrow, xor1, I1_pin):
    """Return a list of symbols which will not have a device absent error on the connection."""
    return [dtype1, dot, qbar_pin, arrow, xor1, dot, I1_pin]


def test_display_device_absent_error_monitor_1(new_semantic_error_handler,
                                               new_scanner, and1):
    """Test the display_device_absent_error method for the monitor."""
    new_semantic_error_handler.display_device_absent_error(
        [and1])
    new_scanner.print_error.assert_called_with(and1, 0,
                                               "Device and1 is not defined")
    assert new_scanner.print_error.call_count == 1


def test_display_device_absent_error_monitor_2(new_semantic_error_handler,
                                               list_display_device_absent_error_monitor_2,
                                               new_scanner, and1):
    new_semantic_error_handler.display_device_absent_error(
        list_display_device_absent_error_monitor_2)
    new_scanner.print_error.assert_called_with(and1, 0,
                                               "Device and1 is not defined")
    assert new_scanner.print_error.call_count == 1


def test_display_device_absent_error_connection_input(new_semantic_error_handler,
                                                      list_display_device_absent_error_connection_input,
                                                      new_scanner, and1, new_parser):
    """Test the display_device_absent_error method for the input connection."""
    parser = new_parser
    # The parser must be initialised for the devices to be built for the
    # errors which check if a device exists or not to be triggered.
    new_semantic_error_handler.display_device_absent_error(
        list_display_device_absent_error_connection_input)
    new_scanner.print_error.assert_called_with(and1, 0,
                                               "Device and1 is not defined")
    assert new_scanner.print_error.call_count == 1


def test_display_device_absent_error_connection_otuput(new_semantic_error_handler,
                                                       list_display_device_absent_error_connection_output,
                                                       new_scanner, and1, xor1,
                                                       new_parser):
    """Test the display_device_absent_error method for the output connection."""
    parser = new_parser
    # The parser must be initialised for the devices to be built for the
    # errors which check if a device exists or not to be triggered.
    new_semantic_error_handler.display_device_absent_error(
        list_display_device_absent_error_connection_output)
    new_scanner.print_error.assert_called_with(and1, 0,
                                               "Device and1 is not defined")
    assert new_scanner.print_error.call_count == 1


def test_display_device_absent_error_no_call(new_semantic_error_handler,
                                             list_display_device_absent_error_connection_no_call,
                                             new_scanner, and1, new_parser):
    """Test the display_device_absent_error method to ensure it does not call print_error."""
    parser = new_parser

    new_semantic_error_handler.display_device_absent_error(
        list_display_device_absent_error_connection_no_call)
    new_scanner.print_error.assert_not_called()
    # If all the devices do exist, then print_error should not be called.


def test_display_not_output_error(new_semantic_error_handler, new_scanner,
                                  qbar_pin, dtype1):
    """Test the display_not_output_error method."""
    new_semantic_error_handler.display_not_output_error(dtype1)
    new_scanner.print_error.assert_called_with(dtype1, 0,
                                               "This is not an output. Only outputs can be monitored.")
    assert new_scanner.print_error.call_count == 1
    # Harder to show the functionality of display_not_output_error here
    # but if it was given say a port such as xor1.QBAR, it would return
    # an error message like this saying that the specific port is not an
    # output.
    new_semantic_error_handler.display_not_output_error(qbar_pin)
    new_scanner.print_error.assert_called_with(qbar_pin, 0,
                                               "This is not an output. Only outputs can be monitored.")
    assert new_scanner.print_error.call_count == 2


def test_display_monitor_present_error(new_semantic_error_handler, new_scanner,
                                       and1):
    """Test the display_monitor_present_error method."""
    new_semantic_error_handler.display_monitor_present_error(and1)
    new_scanner.print_error.assert_called_with(and1, 0,
                                               "Warning: Monitor exists at this output already.")
    assert new_scanner.print_error.call_count == 1


def test_display_input_not_connected_error(new_names, new_devices,
                                           new_monitors, new_network):
    """Test the display_input_not_connected_error method."""
    scanner = Scanner("test_parse_files/semantic_error_7.txt", new_names)
    parser = Parser(new_names, new_devices, new_network, new_monitors, scanner)
    parser.parse_network()
    scanner.print_error = MagicMock()
    symbol = Symbol("I1", 32, 5, 20)
    parser.semantic_error_handler.display_input_not_connected_error(symbol)
    scanner.print_error.assert_called_once_with(symbol, 2,
                                                "The following input pins are not connected to a device: ['dtype1.CLK']")


def test_display_input_not_connected_error_multiple(new_names, new_devices,
                                                    new_monitors, new_network):
    """Test the display_input_not_connected_error method with multiple inputs not connected."""
    scanner = Scanner("test_parse_files/semantic_error_10.txt", new_names)
    parser = Parser(new_names, new_devices, new_network, new_monitors, scanner)
    parser.parse_network()
    scanner.print_error = MagicMock()
    symbol = Symbol("I1", 32, 5, 20)
    parser.semantic_error_handler.display_input_not_connected_error(symbol)
    scanner.print_error.assert_called_once_with(symbol, 2,
                                                "The following input pins are not connected to a device: ['dtype1.CLK', 'xor1.I2']")
