"""Test the devices module."""
import pytest

from scanner import Symbol, Scanner
from names import Names


@pytest.fixture
def new_scanner():
    """Return a new instance of the Scanner class."""
    new_names = Names()
    new_scanner = Scanner("file_for_test_scanner.txt", new_names)
    return new_scanner


@pytest.fixture
def new_list(new_scanner):
    """Return a list of symbols of the given file."""
    new_list = [Symbol("DEVICES", new_scanner.names.lookup(['DEVICES'])[0],
                       1, 1),
                Symbol(":", new_scanner.names.lookup([':'])[0], 1, 8),
                Symbol("SWITCH", new_scanner.names.lookup(['SWITCH'])[0], 1,
                       10),
                Symbol("switch1", new_scanner.names.lookup(['switch1'])[0], 1,
                       17),
                Symbol("1", new_scanner.names.lookup(['1'])[0], 1, 25),
                Symbol(",", new_scanner.names.lookup([','])[0], 1, 26),
                Symbol("XOR", new_scanner.names.lookup(['XOR'])[0], 2, 10),
                Symbol("xor1", new_scanner.names.lookup(['xor1'])[0], 2, 14),
                Symbol(";", new_scanner.names.lookup([';'])[0], 2, 18),
                Symbol("CONNECT", new_scanner.names.lookup(['CONNECT'])[0], 4,
                       1),
                Symbol(":", new_scanner.names.lookup([':'])[0], 4, 8),
                Symbol("switch1", new_scanner.names.lookup(['switch1'])[0], 4,
                       10),
                Symbol(">", new_scanner.names.lookup(['>'])[0], 4, 18),
                Symbol("xor1", new_scanner.names.lookup(['xor1'])[0], 4, 20),
                Symbol(".", new_scanner.names.lookup(['.'])[0], 4, 24),
                Symbol("I1", new_scanner.names.lookup(['I1'])[0], 4, 25),
                Symbol(";", new_scanner.names.lookup([';'])[0], 4, 27),
                Symbol("MONITOR", new_scanner.names.lookup(['MONITOR'])[0], 5,
                       1),
                Symbol(":", new_scanner.names.lookup([':'])[0], 5, 8),
                Symbol("switch1", new_scanner.names.lookup(['switch1'])[0], 5,
                       10),
                Symbol(";", new_scanner.names.lookup([';'])[0], 5, 17),
                Symbol("END", new_scanner.names.lookup(['END'])[0], 6, 1),
                Symbol(";", new_scanner.names.lookup([';'])[0], 6, 4)]
    return new_list


@pytest.fixture
def print_message():
    """Return a list of messages to be printed."""
    # Arrow points at 'X'
    m_1 = "m_1\nLine 2:          XOR xor1;\n                 ^\n"
    # Arrow points at 'i'
    m_2 = "m_2\nLine 4: CONNECT: switch1 > xor1.I1;\n                   ^\n"
    # Arrow points at 'E'
    m_3 = "m_3\nLine 6: END;\n        ^\n"
    return [m_1, m_2, m_3]


def test_reset_symbol_counter(new_scanner):
    """Test if the symbol counter is reset."""
    new_scanner.symbol_counter = 10
    new_scanner.reset_symbol_counter()
    assert new_scanner.symbol_counter == -1


def test_open_file(new_scanner):
    """Test if the file is opened correctly."""
    new_scanner.open_file()
    assert new_scanner.file is not None
    assert new_scanner.file.closed is False


def test_close_file(new_scanner):
    """Test if the file is closed correctly."""
    new_scanner.open_file()
    new_scanner.close_file()
    assert new_scanner.file.closed


def test_get_list_of_symbols(new_scanner, new_list):
    """Test if get_list_of_symbols returns the correct list of symbols."""
    list_of_symbols = new_scanner.get_list_of_symbols()
    for i in range(len(list_of_symbols)):
        assert new_scanner.names.get_name_string(list_of_symbols[i].id) \
            == new_scanner.names.get_name_string(new_list[i].id)


def test_get_symbol(new_scanner, new_list):
    """Test if get_symbol returns the correct symbol."""
    for i in range(len(new_list)):
        assert new_scanner.names.get_name_string(new_scanner.get_symbol().id) \
            == new_scanner.names.get_name_string(new_list[i].id)
    assert new_scanner.get_symbol() is None


def test_print_error(capfd, new_scanner, print_message):
    """Test if print_error prints the correct error message."""
    new_scanner.print_error(new_scanner.list_of_symbols[6], 0, "m_1")
    out, err = capfd.readouterr()
    assert out == print_message[0]
    new_scanner.print_error(new_scanner.list_of_symbols[11], 2, "m_2")
    out, err = capfd.readouterr()
    assert out == print_message[1]
    new_scanner.print_error(new_scanner.list_of_symbols[21], 0, "m_3")
    out, err = capfd.readouterr()
    assert out == print_message[2]
    assert new_scanner.print_error(None, 0, "None") is False
