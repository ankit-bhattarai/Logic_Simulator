"""Test the parse module."""
import pytest
from unittest.mock import MagicMock, call, Mock

from names import Names
from devices import Devices
from network import Network
from monitors import Monitors
from scanner import Scanner, Symbol
from parse import Parser

"""
Methods involved in syntax error processing in Parser:
------------------------------------------------------

check_name - tested through test_name_error_identification
check_clock - tested through test_syntax_error_identification
check_switch  - tested through test_syntax_error_identification
check_logic_device - tested through test_syntax_error_identification
check_dtype_xor - tested through test_syntax_error_identification
device - tested through test_syntax_error_identification
device_list - tested through test_syntax_error_identification
connection - tested through test_syntax_error_identification
connection_list - tested through test_syntax_error_identification
monitor - tested through test_syntax_error_identification
monitor_list - tested through test_syntax_error_identification
display_syntax_error - tested through test_syntax_error_identification
network_dict - tested through test_build_network
"""

syntax_error_types = {
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
    23: "ValueError: Siggen waveform should only consist of 0s and 1s."}


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
    """Test that the correct syntax error (name error) is identified at the correct locations."""
    new_scanner = Scanner(definition_file, new_names)
    new_scanner.print_error = MagicMock()
    new_parser = Parser(new_names,
                        new_devices,
                        new_network,
                        new_monitors,
                        new_scanner)

    new_parser.network_dict()
    expected_calls = []

    for name_error_index, symbol_index, letter_index in zip(name_error_indices,
                                                            error_symbol_indices,
                                                            letter_indices):

        erronous_symbol = new_scanner.list_of_symbols[symbol_index]
        error_message = syntax_error_types[9] + name_errors[name_error_index]
        expected_call = call(erronous_symbol, letter_index, error_message)
        expected_calls.append(expected_call)

    new_scanner.print_error.assert_has_calls(expected_calls, any_order=False)


@pytest.mark.parametrize("early_termination_definition_file",
                         [("test_parse_files/syntax_error_22_a.txt"),
                          ("test_parse_files/syntax_error_22_b.txt"),
                          ("test_parse_files/syntax_error_22_c.txt"),
                          ("test_parse_files/syntax_error_22_d.txt"),
                          ("test_parse_files/syntax_error_22_e.txt"),
                          ("test_parse_files/syntax_error_22_f.txt"),
                          ("test_parse_files/syntax_error_22_g.txt"),
                          ("test_parse_files/syntax_error_22_h.txt")])
def test_early_termination_error_identification(early_termination_definition_file, new_names,
                                                new_devices, new_network,
                                                new_monitors):
    """Test that the correct syntax error is identified when the file ends too early for several
    early termination locations."""
    new_scanner = Scanner(early_termination_definition_file, new_names)
    new_scanner.print_error = MagicMock()
    new_parser = Parser(new_names,
                        new_devices,
                        new_network,
                        new_monitors,
                        new_scanner)

    new_parser.network_dict()

    erronous_symbol = new_scanner.list_of_symbols[-1]
    # Check that the print error function is called only once and with the correct error message/location
    new_scanner.print_error.assert_called_once_with(
        erronous_symbol, 0, syntax_error_types[22])
    # Check that this is the only error that has been accumulated by num of errors
    assert new_parser.num_of_errors == 1


@pytest.mark.parametrize("definition_file, error_type, error_symbol_indices",
                         [("test_parse_files/syntax_error_1.txt", 1, [0]),
                          ("test_parse_files/syntax_error_2.txt", 2, [24]),
                          ("test_parse_files/syntax_error_3.txt", 3, [78]),
                          ("test_parse_files/syntax_error_4.txt", 4, [94]),
                          ("test_parse_files/syntax_error_5.txt", 5, [2]),
                          ("test_parse_files/syntax_error_6.txt",
                           6, [4, 7, 10, 13, 16, 19]),
                          ("test_parse_files/syntax_error_7.txt", 19, [4, 8]),
                          ("test_parse_files/syntax_error_8.txt",
                           8, [2, 6, 10, 14, 18, 22, 26, 29]),
                          ("test_parse_files/syntax_error_10.txt", 10, [4]),
                          ("test_parse_files/syntax_error_11.txt", 11, [4, 8]),
                          ("test_parse_files/syntax_error_12.txt",
                           12, [4, 8, 16]),
                          ("test_parse_files/syntax_error_13.txt", 13, [16]),
                          ("test_parse_files/syntax_error_14.txt", 14, [16]),
                          ("test_parse_files/syntax_error_15.txt",
                           15, [27, 33]),
                          ("test_parse_files/syntax_error_16.txt", 16, [35]),
                          ("test_parse_files/syntax_error_17.txt",
                           17, [30, 36, 42]),
                          ("test_parse_files/syntax_error_18.txt",
                           18, [81, 85, 93]),
                          ("test_parse_files/syntax_error_19.txt",
                           19, [5, 23]),
                          ("test_parse_files/syntax_error_20.txt",
                           20, [1, 79]),
                          ("test_parse_files/syntax_error_21.txt", 21, [95])])
def test_syntax_error_identification(definition_file, error_type, error_symbol_indices,
                                     new_names, new_devices, new_network, new_monitors):
    """Test that the correct syntax error is identified and subsequently sent to the
    scanner for printing.

    By using mock functions, it is tested whether the scanner.print_error
    is being called correctly or not. A benefit of this approach is that the
    scanner.print_error method can be changed in the future without affecting
    these tests at all.
    """
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

    # Assert that the right errors are passed for printing
    new_scanner.print_error.assert_has_calls(expected_calls, any_order=False)
    # Assert that no other errors are passed for printing
    assert new_scanner.print_error.call_count == len(error_symbol_indices)
    # Assert that the internally stored number of errors is correct
    assert new_parser.num_of_errors == len(error_symbol_indices)


@pytest.fixture
def network_dict_1():
    """
    Fixture to populate the expected network dictionary
    for the test file - "test_parse_files/test_build_network_dict_1.txt"
    """
    network_dict = {}  # MAINTENANCE - change to dict
    network_dict['DEVICES'] = [[Symbol("CLOCK", 5, 1, 10),
                               Symbol("clock1", 18, 1, 16),
                               Symbol("10", 19, 1, 23)]]
    network_dict['CONNECT'] = [[Symbol("clock1", 18, 2, 10),
                                Symbol(">", 22, 2, 17),
                                Symbol("and1", 23, 2, 19),
                                Symbol(".", 24, 2, 23),
                                Symbol("I1", 25, 2, 24)]]
    network_dict['MONITOR'] = [[Symbol("and1", 23, 3, 10)]]

    return network_dict


def test_build_network_dict_1(new_names, network_dict_1, new_devices, new_network,
                              new_monitors):
    """Test that the network dictionary, used later to check semantics and
       to build the network, is built correctly - for increasingly complex files
       - through test_build_network_dict_{1, 2, 3}.

       This is the converse of testing for error identification as this dictionary
       is only built when CORRECT syntax is passed. This is different from the above
       tests, for which INCORRECT syntax is passed and error identification is tested.
    """

    new_scanner = Scanner(
        "test_parse_files/test_build_network_dict_1.txt", new_names)
    new_parser = Parser(new_names, new_devices, new_network, new_monitors,
                        new_scanner)

    # Check that the network dictionary is built correctly
    assert new_parser.network_dict() == network_dict_1
    # Check that no errors have been accumulated
    assert new_parser.num_of_errors == 0


@pytest.fixture
def network_dict_2():
    """
    Fixture to populate the expected network dictionary
    for the second test file - "test_parse_files/test_build_network_dict_2.txt"
    """
    network_dict_2 = {}  # MAINTENANCE - change to dict
    network_dict_2["DEVICES"] = [[Symbol("SWITCH", 6, 1, 10), Symbol("switch1", 18, 1, 17), Symbol("0", 19, 1, 25)],
                                 [Symbol("SWITCH", 6, 1, 28), Symbol(
                                     "switch2", 21, 1, 35), Symbol("0", 19, 1, 43)],
                                 [Symbol("AND", 0, 1, 46), Symbol(
                                     "and1", 22, 1, 50), Symbol("2", 23, 1, 55)],
                                 [Symbol("OR", 1, 1, 58), Symbol(
                                     "or1", 24, 1, 61), Symbol("2", 23, 1, 65)],
                                 [Symbol("NAND", 2, 1, 68), Symbol("nand1", 25, 1, 73), Symbol("2", 23, 1, 79)]]
    network_dict_2['CONNECT'] = [[Symbol("switch1", 18, 2, 10), Symbol(">", 28, 2, 18), Symbol("and1", 22, 2, 20),
                                  Symbol(".", 29, 2, 24), Symbol("I1", 30, 2, 25)], [Symbol("switch1", 18, 2, 29),
                                                                                     Symbol(">", 28, 2, 37), Symbol(
                                                                                         "or1", 24, 2, 39), Symbol(".", 29, 2, 42),
                                                                                     Symbol("I1", 30, 2, 43)], [Symbol("switch2", 21, 2, 47), Symbol(">", 28, 2, 55),
                                                                                                                Symbol("and1", 22, 2, 57), Symbol(".", 29, 2, 61), Symbol("I2", 31, 2, 62)],
                                 [Symbol("switch2", 21, 2, 66), Symbol(">", 28, 2, 74), Symbol("or1", 24, 2, 76),
                                  Symbol(".", 29, 2, 79), Symbol("I2", 31, 2, 80)], [Symbol("and1", 22, 3, 2),
                                                                                     Symbol(">", 28, 3, 7), Symbol(
                                      "nand1", 25, 3, 9), Symbol(".", 29, 3, 14),
        Symbol("I1", 30, 3, 15)], [Symbol("or1", 24, 3, 19), Symbol(">", 28, 3, 23),
                                   Symbol("nand1", 25, 3, 25), Symbol(".", 29, 3, 30), Symbol("I2", 31, 3, 31)]]
    network_dict_2['MONITOR'] = [[Symbol("and1", 22, 4, 10)], [Symbol(
        "or1", 24, 4, 16)], [Symbol("nand1", 25, 4, 21)]]

    return network_dict_2


def test_build_network_dict_2(network_dict_2, new_names, new_devices, new_network, new_monitors):
    new_scanner = Scanner(
        "test_parse_files/test_build_network_dict_2.txt", new_names)
    new_parser = Parser(new_names,
                        new_devices,
                        new_network,
                        new_monitors,
                        new_scanner)

    # Check that the second test network dictionary is built correctly
    assert new_parser.network_dict() == network_dict_2
    # Check that no errors have been accumulated
    assert new_parser.num_of_errors == 0


@pytest.fixture
def network_dict_3():
    """
    Fixture to populate the expected network dictionary
    for the third test file - "test_parse_files/test_build_network_dict_3.txt"
    """
    network_dict_3 = {}  # MAINTENANCE - change to dict
    network_dict_3['DEVICES'] = [[Symbol("SWITCH", 6, 1, 10), Symbol("switch1", 18, 1, 17), Symbol("1", 19, 1, 25)],
                                 [Symbol("SWITCH", 6, 1, 28), Symbol(
                                     "switch2", 21, 1, 35), Symbol("0", 22, 1, 43)],
                                 [Symbol("CLOCK", 5, 1, 46), Symbol(
                                     "clock1", 23, 1, 52), Symbol("2", 24, 1, 59)],
                                 [Symbol("DTYPE", 7, 1, 62), Symbol("dtype1", 25, 1, 68)], [Symbol("NOR", 3, 2, 10),
                                                                                            Symbol("nor1", 26, 2, 14), Symbol("2", 24, 2, 19)], [Symbol("XOR", 4, 2, 22),
                                                                                                                                                 Symbol("xor1", 27, 2, 26)]]
    network_dict_3['CONNECT'] = [[Symbol("switch1", 18, 3, 10), Symbol(">", 30, 3, 18), Symbol("dtype1", 25, 3, 20),
                                  Symbol(".", 31, 3, 26), Symbol("DATA", 13, 3, 27)], [Symbol("switch1", 18, 3, 33),
                                                                                       Symbol(">", 30, 3, 41), Symbol(
                                                                                           "dtype1", 25, 3, 43), Symbol(".", 31, 3, 49),
                                                                                       Symbol("SET", 11, 3, 50)], [Symbol("switch1", 18, 3, 55), Symbol(">", 30, 3, 63),
                                                                                                                   Symbol("nor1", 26, 3, 65), Symbol(".", 31, 3, 69), Symbol("I1", 32, 3, 70)],
                                 [Symbol("switch2", 21, 4, 1), Symbol(">", 30, 4, 9), Symbol("dtype1", 25, 4, 11),
                                  Symbol(".", 31, 4, 17), Symbol("CLEAR", 12, 4, 18)], [Symbol("switch2", 21, 4, 25),
                                                                                        Symbol(">", 30, 4, 33), Symbol(
                                                                                            "xor1", 27, 4, 35), Symbol(".", 31, 4, 39),
                                                                                        Symbol("I2", 33, 4, 40)], [Symbol("dtype1", 25, 4, 44), Symbol(".", 31, 4, 50),
                                                                                                                   Symbol("Q", 14, 4, 51), Symbol(
                                                                                                                       ">", 30, 4, 53), Symbol("nor1", 26, 4, 55),
                                                                                                                   Symbol(".", 31, 4, 59), Symbol("I2", 33, 4, 60)], [Symbol("dtype1", 25, 5, 1),
                                                                                                                                                                      Symbol(".", 31, 5, 7), Symbol(
                                                                                                                       "QBAR", 15, 5, 8), Symbol(">", 30, 5, 13),
        Symbol("xor1", 27, 5, 15), Symbol(".", 31, 5, 19), Symbol("I1", 32, 5, 20)],
        [Symbol("clock1", 23, 5, 24), Symbol(">", 30, 5, 31), Symbol("dtype1", 25, 5, 33),
         Symbol(".", 31, 5, 39), Symbol("CLK", 10, 5, 40)]]
    network_dict_3['MONITOR'] = [[Symbol("switch1", 18, 6, 10)], [Symbol("clock1", 23, 6, 19)], [Symbol("switch2", 21, 6, 27)],
                                 [Symbol("dtype1", 25, 6, 36), Symbol(
                                     ".", 31, 6, 42), Symbol("Q", 14, 6, 43)],
                                 [Symbol("nor1", 26, 6, 46)], [Symbol("xor1", 27, 6, 52)]]

    return network_dict_3


def test_build_network_dict_3(network_dict_3, new_names, new_devices, new_network, new_monitors):
    new_scanner = Scanner(
        "test_parse_files/test_build_network_dict_3.txt", new_names)
    new_parser = Parser(new_names,
                        new_devices,
                        new_network,
                        new_monitors,
                        new_scanner)

    # Check that the third test network dictionary is built correctly
    assert new_parser.network_dict() == network_dict_3
    # Check that no errors have been accumulated
    assert new_parser.num_of_errors == 0


@pytest.mark.parametrize("definition_file, symbol_details, message, index, success",
                         [("test_parse_files/semantic_error_1.txt", ["switch1", 18, 1, 35],
                           "Device names are not unique. switch1 is already the name of a device", 0, False),
                          ("test_parse_files/semantic_error_2.txt", ["switch3", 32, 4, 33],
                          "Device switch3 is not defined", 0, False),
                          ("test_parse_files/semantic_error_3.txt", ["I3", 32, 4, 70],
                           "Port I3 is not defined for device nor1", 0, False),
                          ("test_parse_files/semantic_error_4.txt", ["I1", 32, 4, 18],
                           "Port I1 is not defined for device dtype1", 0, False),
                          ("test_parse_files/semantic_error_5.txt", ["DATA", 13, 5, 62],
                           "Signal switch1 is already connected to the input pin dtype1.DATA. Only one signal must be connected to an input.", 0, False),
                          ("test_parse_files/semantic_error_6.txt", ["DATA", 13, 5, 62],
                           "Signal switch1 is already connected to the input pin dtype1.DATA. Only one signal must be connected to an input.", 0, False),
                          ("test_parse_files/semantic_error_7.txt", ["I1", 32, 5, 20],
                           "The following input pins are not connected to a device: ['dtype1.CLK']", 2, False),
                          ("test_parse_files/semantic_error_8.txt", ["dtype1", 25, 4, 44],
                           "Port is missing for device dtype1", 0, False),
                          ("test_parse_files/semantic_error_9.txt", ["QBAR", 15, 5, 50],
                           "Port QBAR is not defined for device xor1", 0, False),
                          ("test_parse_files/semantic_error_10.txt", ["I1", 32, 5, 20],
                           "The following input pins are not connected to a device: ['dtype1.CLK', 'xor1.I2']", 2, False),
                          ("test_parse_files/semantic_error_11.txt", ["xor2", 35, 6, 52],
                           "Device xor2 is not defined", 0, False),
                          ("test_parse_files/semantic_error_12.txt", ["QBAR", 15, 6, 57],
                             "This is not an output. Only outputs can be monitored.", 0, False),
                          ("test_parse_files/semantic_error_13.txt", ["dtype1", 25, 6, 36],
                             "This is not an output. Only outputs can be monitored.", 0, False),
                             ("test_parse_files/semantic_error_14.txt", ["Q", 14, 6, 59],
                              "Warning: Monitor exists at this output already.", 0, True)
                          ]
                         )
def test_semantic_error_identification(definition_file, symbol_details,
                                       message, index, success, new_names, new_devices,
                                       new_network, new_monitors):
    """Test that the correct semantic error is identified.

    This method tests that the correct semantic errors are identified and sent
    to the print_error method of the scanner.

    By using mock functions, it is tested whether the scanner.print_error
    is being called correctly or not. A benefit of this approach is that the
    scanner.print_error method can be changed in the future without affecting
    these tests at all. Were this test to do a print assert check, if
    print_error was changed for aesthetic or functionality reasons, all of
    these tests will have to be rewritten to suit the new style in which
    the mesaages are printed. The cost for this approach however is that the
    definition files have to be analysed to get the attributes of the symbol.
    """
    new_scanner = Scanner(definition_file, new_names)
    new_scanner.print_error = MagicMock()
    new_parser = Parser(new_names, new_devices, new_network, new_monitors,
                        new_scanner)
    result = new_parser.parse_network()
    assert result == success
    symbol = Symbol(*symbol_details)
    new_scanner.print_error.assert_called_once_with(symbol, index, message)
    assert new_scanner.print_error.call_count == 1


@pytest.fixture
def get_def_1_parser(new_names, new_devices, new_monitors, new_network):
    """Returns a parser for the def1.txt file."""
    new_scanner = Scanner("test_parse_files/def1.txt", new_names)
    new_parser = Parser(new_names, new_devices, new_network, new_monitors,
                        new_scanner)
    return new_parser


def test_build_devices_1(new_names, new_devices, get_def_1_parser):
    """Tests the build devices method with a valid file and checks it calls make_device correctly."""
    new_parser = get_def_1_parser
    network_dict = new_parser.network_dict()
    new_devices.make_device = Mock()
    new_parser.build_devices(network_dict["DEVICES"])
    switch1_call = call(*new_names.lookup(["switch1", "SWITCH"]), '0')
    switch2_call = call(*new_names.lookup(["switch2", "SWITCH"]), '0')
    and1_call = call(*new_names.lookup(["and1", "AND"]), '2')
    or1_call = call(*new_names.lookup(["or1", "OR"]), '2')
    nand1_call = call(*new_names.lookup(["nand1", "NAND"]), '2')
    expected_calls = [switch1_call, switch2_call, and1_call, or1_call,
                      nand1_call]
    new_devices.make_device.assert_has_calls(expected_calls, any_order=False)


def test_build_devices_1_success(get_def_1_parser):
    """Tests the build devices method with a valid file and checks it returns True."""
    new_parser = get_def_1_parser
    network_dict = new_parser.network_dict()
    result = new_parser.build_devices(network_dict["DEVICES"])
    assert result


@pytest.fixture
def get_def_2_parser(new_names, new_devices, new_monitors, new_network):
    """Returns a parser for the def2.txt file."""
    new_scanner = Scanner("test_parse_files/def2.txt", new_names)
    new_parser = Parser(new_names, new_devices, new_network, new_monitors,
                        new_scanner)
    return new_parser


def test_build_devices_2(new_names, new_devices, get_def_2_parser):
    """Tests the build devices method with a different valid file and checks it calls make_device correctly."""
    new_parser = get_def_2_parser
    network_dict = new_parser.network_dict()
    new_devices.make_device = Mock()
    new_parser.build_devices(network_dict["DEVICES"])
    switch1_call = call(*new_names.lookup(["switch1", "SWITCH"]), '1')
    switch2_call = call(*new_names.lookup(["switch2", "SWITCH"]), '0')
    clock1_call = call(*new_names.lookup(["clock1", "CLOCK"]), '2')
    dtype1_call = call(*new_names.lookup(["dtype1", "DTYPE"]), None)
    nor1_call = call(*new_names.lookup(["nor1", "NOR"]), '2')
    xor1_call = call(*new_names.lookup(["xor1", "XOR"]), None)
    expected_calls = [switch1_call, switch2_call, clock1_call, dtype1_call,
                      nor1_call, xor1_call]
    new_devices.make_device.assert_has_calls(expected_calls, any_order=False)


@pytest.fixture
def get_semantic_error_1_parser(new_names, new_devices, new_monitors,
                                new_network):
    """Returns a parser for the semantic_error_1.txt file."""
    new_scanner = Scanner("test_parse_files/semantic_error_1.txt", new_names)
    new_parser = Parser(new_names, new_devices, new_network, new_monitors,
                        new_scanner)
    return new_parser


def test_build_devices_quit_1(get_semantic_error_1_parser):
    """Tests the build devices method with a file that has a semantic error and checks it returns False."""
    new_parser = get_semantic_error_1_parser
    network_dict = new_parser.network_dict()
    success = new_parser.build_devices(network_dict["DEVICES"])
    assert not success


def test_build_devices_order_quit_2(new_names, new_devices,
                                    get_semantic_error_1_parser):
    """Tests the build devices method with a file that has a semantic error and checks it quits at the first error."""
    new_parser = get_semantic_error_1_parser
    network_dict = new_parser.network_dict()
    new_devices.make_device = Mock()
    new_parser.build_devices(network_dict["DEVICES"])
    switch1_call = call(*new_names.lookup(["switch1", "SWITCH"]), '1')
    switch1_dup_call = call(*new_names.lookup(["switch1", "SWITCH"]), '0')
    expected_calls = [switch1_call, switch1_dup_call]
    new_devices.make_device.assert_has_calls(expected_calls, any_order=False)


def test_build_connections_1(new_names, new_devices, get_def_1_parser):
    """Tests the build connections method with a valid file and checks it calls make_connection correctly."""
    new_parser = get_def_1_parser
    network_dict = new_parser.network_dict()
    new_devices.make_connection = Mock()
    # Ensure that the build devices method is called first
    new_parser.build_devices(network_dict["DEVICES"])
    new_parser.build_connections(network_dict["CONNECT"])

    connection_1 = call(*new_names.lookup(["switch1", None, "and1", "I1"]), 0)
    connection_2 = call(*new_names.lookup(["switch1", None, "or1", "I1"]), 0)
    connection_3 = call(*new_names.lookup(["switch2", None, "and1", "I2"]), 0)
    connection_4 = call(*new_names.lookup(["switch2", None, "or1", "I2"]), 0)
    connection_5 = call(*new_names.lookup(["and1", None, "nand1", "I1"]), 0)
    connection_6 = call(*new_names.lookup(["or1", None, "nand1", "I2"]), 0)

    expected_calls = [connection_1, connection_2, connection_3, connection_4,
                      connection_5, connection_6]

    expected_calls = []
    new_devices.make_connection.assert_has_calls(expected_calls,
                                                 any_order=False)


def test_build_connections_1_success(get_def_1_parser):
    """Tests the build connections method with a valid file and checks it returns True."""
    new_parser = get_def_1_parser
    network_dict = new_parser.network_dict()
    # Ensure that the build devices method is called first
    new_parser.build_devices(network_dict["DEVICES"])
    # Check that the build connections method returns True
    result = new_parser.build_connections(network_dict["CONNECT"])
    assert result


def test_build_connections_2(new_names, new_devices, get_def_2_parser):
    """Tests the build connections method with a valid file and checks it calls make_connection correctly."""
    new_parser = get_def_2_parser
    network_dict = new_parser.network_dict()
    new_devices.make_connection = Mock()
    # Ensure that the build devices method is called first
    new_parser.build_devices(network_dict["DEVICES"])
    new_parser.build_connections(network_dict["CONNECT"])

    connection_1 = call(
        *new_names.lookup(["switch1", None, "dtype1", "DATA"]), 0)
    connection_2 = call(
        *new_names.lookup(["switch1", None, "dtype1", "SET"]), 0)
    connection_3 = call(*new_names.lookup(["switch1", None, "nor1", "I1"]), 0)
    connection_4 = call(
        *new_names.lookup(["switch2", None, "dtype1", "CLEAR"]), 0)
    connection_5 = call(*new_names.lookup(["switch2", None, "xor1", "I2"]), 0)
    connection_6 = call(*new_names.lookup(["dtype1", "Q", "nor1", "I2"]), 0)
    connection_7 = call(*new_names.lookup(["dtype1", "QBAR", "xor1", "I1"]), 0)
    connection_8 = call(
        *new_names.lookup(["clock1", None, "dtype1", "CLK"]), 0)
    expected_calls = [connection_1, connection_2, connection_3, connection_4,
                      connection_5, connection_6, connection_7, connection_8]

    expected_calls = []
    new_devices.make_connection.assert_has_calls(expected_calls,
                                                 any_order=False)


def test_build_connections_2_success(get_def_2_parser):
    """Tests the build connections method with a valid file and checks it returns True."""
    new_parser = get_def_2_parser
    network_dict = new_parser.network_dict()
    # Ensure that the build devices method is called first
    new_parser.build_devices(network_dict["DEVICES"])
    # Check that the build connections method returns True
    result = new_parser.build_connections(network_dict["CONNECT"])
    assert result


@pytest.fixture
def get_semantic_error_5_parser(new_names, new_devices, new_monitors,
                                new_network):
    """Returns a parser for the semantic_error_5.txt file."""
    new_scanner = Scanner("test_parse_files/semantic_error_5.txt", new_names)
    new_parser = Parser(new_names, new_devices, new_network, new_monitors,
                        new_scanner)
    return new_parser


def test_build_connections_quit_5(get_semantic_error_5_parser):
    """Tests the build connections method with a file that has a semantic error in the connections
    and checks that it returns False"""
    new_parser = get_semantic_error_5_parser
    network_dict = new_parser.network_dict()
    # Ensure that the build devices method is called first
    new_parser.build_devices(network_dict["DEVICES"])
    # Check that the build connections method returns True
    success = new_parser.build_connections(network_dict["CONNECT"])
    assert not success


def test_build_monitors_1(new_names, new_monitors, get_def_1_parser):
    """Tests the build monitors method with a valid file and checks it calls make_monitors correctly."""
    new_parser = get_def_1_parser
    network_dict = new_parser.network_dict()
    new_monitors.make_monitor = Mock()
    new_parser.build_devices(network_dict["DEVICES"])
    new_parser.build_connections(network_dict["CONNECT"])
    new_parser.build_monitors(network_dict["MONITOR"])

    monitor_1 = call(new_names.query("and1"), None)
    monitor_2 = call(new_names.query("or1"), None)
    monitor_3 = call(new_names.query("nand1"), None)

    expected_calls = [monitor_1, monitor_2, monitor_3]
    new_monitors.make_monitor.assert_has_calls(expected_calls,
                                               any_order=False)


def test_build_monitors_1_success(get_def_1_parser):
    """Tests the build monitors method with a valid file and checks it returns True."""
    new_parser = get_def_1_parser
    network_dict = new_parser.network_dict()

    new_parser.build_devices(network_dict["DEVICES"])
    new_parser.build_connections(network_dict["CONNECT"])
    assert new_parser.build_monitors(network_dict["MONITOR"])


def test_build_monitors_2(new_names, new_monitors, get_def_2_parser):
    """Tests the build monitors method with a valid file and checks it calls make_monitors correctly."""
    new_parser = get_def_2_parser
    network_dict = new_parser.network_dict()
    new_monitors.make_monitor = Mock()
    new_parser.build_devices(network_dict["DEVICES"])
    new_parser.build_connections(network_dict["CONNECT"])
    new_parser.build_monitors(network_dict["MONITOR"])

    monitor_1 = call(new_names.query("switch1"), None)
    monitor_2 = call(new_names.query("clock1"), None)
    monitor_3 = call(new_names.query("switch2"), None)
    monitor_4 = call(new_names.query("dtype1"), new_names.query("Q"))
    monitor_5 = call(new_names.query("nor1"), None)
    monitor_6 = call(new_names.query("xor1"), None)

    expected_calls = [monitor_1, monitor_2, monitor_3,
                      monitor_4, monitor_5, monitor_6]

    new_monitors.make_monitor.assert_has_calls(expected_calls,
                                               any_order=False)


def test_build_monitors_2_success(get_def_2_parser):
    """Tests the build monitors method with a valid file and checks it returns True."""
    new_parser = get_def_2_parser
    network_dict = new_parser.network_dict()

    new_parser.build_devices(network_dict["DEVICES"])
    new_parser.build_connections(network_dict["CONNECT"])
    assert new_parser.build_monitors(network_dict["MONITOR"])


@pytest.fixture
def get_semantic_error_12_parser(new_names, new_devices, new_monitors, new_network):
    """Returns a parser for the semantic_error_12.txt file."""
    new_scanner = Scanner("test_parse_files/semantic_error_12.txt", new_names)
    new_parser = Parser(new_names, new_devices, new_network, new_monitors,
                        new_scanner)
    return new_parser


def test_build_monitors_quit_12(get_semantic_error_12_parser):
    """Tests the build monitors method with a file that has a semantic error in the monitors
    and checks that it returns False"""
    new_parser = get_semantic_error_12_parser
    network_dict = new_parser.network_dict()
    new_parser.build_devices(network_dict["DEVICES"])
    new_parser.build_connections(network_dict["CONNECT"])
    success = new_parser.build_monitors(network_dict["MONITOR"])
    assert not success


def test_build_monitors_order_quit_12(new_names, new_monitors, get_semantic_error_12_parser):
    """Tests the build monitors method with a file that has a semantic error in the monitors
    and checks that it adds monitors up until the error by monitoring the make_monitor method"""

    new_parser = get_semantic_error_12_parser
    network_dict = new_parser.network_dict()
    new_monitors.make_monitor = Mock()
    new_parser.build_devices(network_dict["DEVICES"])
    new_parser.build_connections(network_dict["CONNECT"])
    new_parser.build_monitors(network_dict["MONITOR"])

    monitor_1 = call(new_names.query("switch1"), None)
    monitor_2 = call(new_names.query("clock1"), None)
    monitor_3 = call(new_names.query("switch2"), None)
    monitor_4 = call(new_names.query("dtype1"), new_names.query("Q"))
    monitor_5 = call(new_names.query("nor1"), None)

    expected_calls = [monitor_1, monitor_2, monitor_3,
                      monitor_4, monitor_5]

    new_monitors.make_monitor.assert_has_calls(expected_calls,
                                               any_order=False)
