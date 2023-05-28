"""Test the semantic_error_handling module."""
import pytest

from names import Names
from devices import Devices
from network import Network
from monitors import Monitors
from scanner import Scanner, Symbol
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
    return Scanner("file_for_test_semantic_error_handling.txt", new_names)


@pytest.fixture
def new_semantic_error_handler(new_names, new_devices, new_network, new_monitors, new_scanner):
    """Return a new semantic error handler instance."""
    return SemanticErrorHandler(new_names, new_devices, new_network, new_monitors, new_scanner)


@pytest.fixture
def switch1():
    """Return a switch symbol."""
    return Symbol('switch1', 16, 1, 17)


@pytest.fixture
def arrow():
    """Return an arrow symbol."""
    return Symbol('>', 28, 4, 18)


@pytest.fixture
def dtype1():
    """Return a dtype symbol."""
    return Symbol('dtype1', 23, 1, 68)


@pytest.fixture
def dot():
    """Return a dot symbol."""
    return Symbol('.', 29, 4, 26)


@pytest.fixture
def data_pin():
    """Return a data pin symbol."""
    return Symbol('DATA', 11, 4, 27)


@pytest.fixture
def qbar_pin():
    """Return a qbar pin symbol."""
    return Symbol('QBAR', 13, 6, 8)


@pytest.fixture
def xor1():
    """Return an xor symbol."""
    return Symbol('xor1', 25, 5, 35)


@pytest.fixture
def I1_pin():
    """Return an I1 pin symbol."""
    return Symbol('I1', 30, 4, 70)


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
