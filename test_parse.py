"""Test the parse module."""
import pytest
from unittest.mock import MagicMock, call

from names import Names
from devices import Devices
from network import Network
from monitors import Monitors
from scanner import Scanner
from parse import Parser

"""
Methods involved in syntax error processing:

- check_name - tested through test_name_error_identification
- check_clock - tested through test_syntax_error_identification
- check_switch  - tested through test_syntax_error_identification
- check_logic_device - tested through test_syntax_error_identification
- check_dtype_xor - tested through test_syntax_error_identification
- device - tested through test_syntax_error_identification
- device_list - tested through test_syntax_error_identification
- connection - tested through test_syntax_error_identification
- connection_list - tested through test_syntax_error_identification
- monitor - tested through test_syntax_error_identification
- monitor_list - tested through test_syntax_error_identification
- display_syntax_error - tested through test_syntax_error_identification
- network_dict - tested through test_build_network
"""

syntax_error_types = {
    1: "NameError: File should start with keyword 'DEVICES'",
    2: "NameError: ';' after the last device should be followed by keyword 'CONNECT'.",
    3: "NameError: ';' after the last connection should be followed by keyword 'MONITOR'.",
    4: "NameError: ';' after the last monitor should be followed by keyword 'END'.",
    5: "ValueError: There should be at least one device.",
    6: "ValueError: The required number of parameters for a device of the type CLOCK/SWITCH/AND/OR/NAND/NOR is 3. Should also check for incorrect placement or missing punctuations.",
    7: "ValueError: The required number of parameters for a device of the type XOR/DTYPE is 2. Should also check for incorrect placement or missing punctuations.",
    8: "NameError: 1st parameter of a device should be the keyword for that device.",
    9: "TypeError: Device name should be a lowercase alphanumeric string (including '_').",
    10: "ValueError: Clock speed should be a positive integer.",
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
    22: "RuntimeError: File ends too early. Should check for missing sections."}


name_errors = ['First character is not a lowercase letter',
               'Specific character is not a letter, digit or underscore',
               'Specific character is not lowercase']


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


@pytest.mark.parametrize("definition_file, name_error_indices, error_symbol_indices, letter_indices",
                         [("test_parse_files/syntax_error_9.txt", [1, 0, 2], [3, 7, 11], [7, 0, 1])])
def test_name_error_identification(definition_file, name_error_indices, error_symbol_indices,
                                   letter_indices, new_names, new_devices, new_network, new_monitors):
    """Test that the correct syntax error is identified."""
    new_scanner = Scanner(definition_file, new_names)
    new_scanner.print_error = MagicMock()
    new_parser = Parser(
        new_names,
        new_devices,
        new_network,
        new_monitors,
        new_scanner)

    new_parser.network_dict()
    expected_calls = []

    for name_error_index, symbol_index, letter_index in zip(name_error_indices,
                                                            error_symbol_indices,
                                                            letter_indices):
        print(name_error_index)
        erronous_symbol = new_scanner.list_of_symbols[symbol_index]
        error_message = syntax_error_types[9] + name_errors[name_error_index]
        expected_call = call(erronous_symbol, letter_index, error_message)
        expected_calls.append(expected_call)

    new_scanner.print_error.assert_has_calls(expected_calls, any_order=False)


@pytest.mark.parametrize("definition_file", 
                         [("test_parse_files/syntax_error_22_a.txt"),
                         ("test_parse_files/syntax_error_22_b.txt"),
                         ("test_parse_files/syntax_error_22_c.txt"),
                         ("test_parse_files/syntax_error_22_d.txt"),
                         ("test_parse_files/syntax_error_22_e.txt"),
                         ("test_parse_files/syntax_error_22_f.txt"),
                         ("test_parse_files/syntax_error_22_g.txt"),
                         ("test_parse_files/syntax_error_22_h.txt")])


def test_early_termination_error_identification(definition_file, new_names, 
                                                new_devices, new_network, 
                                                new_monitors):
    """
    Test that the correct syntax error is identified when the file ends too early for several early termination locations.
    """
    new_scanner = Scanner(definition_file, new_names)
    new_scanner.print_error = MagicMock()
    new_parser = Parser(new_names,
                        new_devices,
                        new_network,
                        new_monitors,
                        new_scanner)

    new_parser.network_dict()

    erronous_symbol = new_scanner.list_of_symbols[-1]
    new_scanner.print_error.assert_called_once_with(erronous_symbol, 0, syntax_error_types[22])


@pytest.mark.parametrize("definition_file, error_type, error_symbol_indices",
                         [("test_parse_files/syntax_error_1.txt", 1, [0]),
                          ("test_parse_files/syntax_error_2.txt", 2, [24]),
                          ("test_parse_files/syntax_error_3.txt", 3, [78]),
                          ("test_parse_files/syntax_error_4.txt", 4, [94]),
                          ("test_parse_files/syntax_error_5.txt", 5, [2]),
                          ("test_parse_files/syntax_error_6.txt", 6, [4, 7, 10, 13, 16, 19]),
                          ("test_parse_files/syntax_error_7.txt", 19, [4, 8]),
                          ("test_parse_files/syntax_error_8.txt", 8, [2, 6, 10, 14, 18, 22, 26, 29]),
                          ("test_parse_files/syntax_error_10.txt", 10, [4]),
                          ("test_parse_files/syntax_error_11.txt", 11, [4, 8]),
                          ("test_parse_files/syntax_error_12.txt",12, [4, 8, 16]),
                          ("test_parse_files/syntax_error_13.txt", 13, [16]),
                          ("test_parse_files/syntax_error_14.txt", 14, [16]),
                          ("test_parse_files/syntax_error_15.txt", 15, [27, 33]),
                          ("test_parse_files/syntax_error_16.txt", 16, [35]),
                          ("test_parse_files/syntax_error_17.txt", 17, [30, 36, 42]),
                          ("test_parse_files/syntax_error_18.txt", 18, [81, 85, 93]),
                          ("test_parse_files/syntax_error_19.txt", 19, [5, 23]),
                          ("test_parse_files/syntax_error_20.txt", 20, [1, 79]),
                          ("test_parse_files/syntax_error_21.txt", 21, [95])])


def test_syntax_error_identification(definition_file, error_type, error_symbol_indices,
                                     new_names, new_devices, new_network, new_monitors):
    """Test that the correct syntax error is identified."""
    new_scanner = Scanner(definition_file, new_names)
    new_scanner.print_error = MagicMock()
    new_parser = Parser(new_names,
                        new_devices,
                        new_network,
                        new_monitors,
                        new_scanner)

    new_parser.network_dict()
    expected_calls = []

    for symbol_index in error_symbol_indices:
        erronous_symbol = new_scanner.list_of_symbols[symbol_index]
        error_message = syntax_error_types[error_type]
        expected_call = call(erronous_symbol, 0, error_message)
        expected_calls.append(expected_call)

    # Assert that the right errors are passed for printings
    new_scanner.print_error.assert_has_calls(expected_calls, any_order=False)
    # Assert that no other errors are passed for printing
    assert new_scanner.print_error.call_count == len(error_symbol_indices)



def test_build_network_dict_1(new_names, new_devices, new_network, new_monitors):
    """Test that the network dictionary, used later to check semantics and
        to build the network, is built correctly."""

def test_build_network_dict_2(new_names, new_devices, new_network, new_monitors):
    """Test that the network dictionary, used later to check semantics and
        to build the network, is built correctly."""
    

def test_build_network_dict_3(new_names, new_devices, new_network, new_monitors):
    """Test that the network dictionary, used later to check semantics and
        to build the network, is built correctly."""


def test_build_network_dict_4(new_names, new_devices, new_network, new_monitors):
    """Test that the network dictionary, used later to check semantics and
        to build the network, is built correctly."""


def test_build_network_dict_5(new_names, new_devices, new_network, new_monitors):
    """Test that the network dictionary, used later to check semantics and
        to build the network, is built correctly."""


def test_identify_total_errors(new_names, new_devices, new_network, new_monitors):
    """Test that the total number of errors is identified correctly."""
    # 5 clean, 5 unclean
