"""Test the symnols class."""
import pytest

from scanner import Symbol


@pytest.fixture
def new_symbol():
    """Return a new symbols instance."""
    return Symbol('A_', 0, 1, 2)


def test_initialise(new_symbol):
    """Test if the symbol is initialised correctly."""
    assert new_symbol.id == 0
    assert new_symbol.type == 'string'
    assert new_symbol.line_number == 1
    assert new_symbol.column_number == 2


@pytest.mark.parametrize("string, expected_bool", [
    ('Hello_1', True),
    ('hello1.', False),
    ('hel@lo1', False),
    ('h ello_1', False)
])
def test_is_string(new_symbol, string, expected_bool):
    """Test if is_string returns the expected boolean."""
    assert new_symbol.is_string(string) == expected_bool


@pytest.mark.parametrize("string, expected_bool", [
    ('Hello_1', False),
    ('hello_1', True),
    ('hel@lo1', False),
    ('h ello_1', False)
])
def test_is_name(new_symbol, string, expected_bool):
    """Test if is_name returns the expected boolean."""
    assert new_symbol.is_name(string) == expected_bool


@pytest.mark.parametrize("string, expected_bool", [
    ('Hello_1', False),
    ('08230', True),
    ('182?30', False),
    ('1 8230', False)
])
def test_is_number(new_symbol, string, expected_bool):
    """Test if is_number returns the expected boolean."""
    assert new_symbol.is_number(string) == expected_bool


@pytest.mark.parametrize("string, expected_bool", [
    ('Hello_1', False),
    ('18230', True),
    ('08230', False),
    ('182?30', False),
    ('1 8230', False)
])
def test_is_integer(new_symbol, string, expected_bool):
    """Test if is_integer returns the expected boolean."""
    assert new_symbol.is_integer(string) == expected_bool


@pytest.mark.parametrize("string, expected_output", [
    ('I13', 'input_pin'),
    ('DATA', 'input_pin'),
    ('QBAR', 'output_pin'),
    ('CONNECT', 'keyword'),
    ('08230', 'number'),
    ('18230', 'integer'),
    ('Hello_1', 'string'),
    ('hello_1', 'name'),
    ('>', 'arrow'),
    ('(', 'other'),
    ('I19', 'string'),
    (' ', 'other')
])
def test_determine_type(new_symbol, string, expected_output):
    """Test if determine_type returns the expected string."""
    assert new_symbol.determine_type(string) == expected_output


@pytest.mark.parametrize("string, expected_output", [
    ('a', None),
    ('a1', None),
    ('a_1', None),
    ('1a', (0, 1)),
    ('_a', (0, 1)),
    ('aA', (1, 3)),
    ('a_1AB', (3, 3)),
    ('a!a', (1, 2))
])
def test_index_not_name(new_symbol, string, expected_output):
    """Test if index_not_name returns the expected tuple."""
    assert new_symbol.index_not_name(string) == expected_output
