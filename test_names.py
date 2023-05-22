"""Test the names module."""
import pytest

from names import Names


@pytest.fixture
def new_names():
    """Return a new names instance."""
    return Names()


@pytest.fixture
def name_string_list():
    """Return a list of example names."""
    return ["Alice", "Bob", "Eve"]


@pytest.fixture
def used_names(name_string_list):
    """Return a names instance, after three names have been added."""
    my_name = Names()
    my_name.lookup(name_string_list)
    my_name.error_code_count = 2
    return my_name


def test_unique_error_codes(used_names):
    """Test if get_string returns the expected string."""
    assert used_names.unique_error_codes(3) == range(2, 5)
    with pytest.raises(TypeError):
        used_names.get_name_string('hello')


@pytest.mark.parametrize("name_id, expected_string", [
    (0, "Alice"),
    (1, "Bob"),
    (2, "Eve"),
    (3, None)
])
def test_get_name_string(used_names, new_names, name_id, expected_string):
    """Test if get_string returns the expected string."""
    # Name is present
    assert used_names.get_name_string(name_id) == expected_string
    # Name is absent
    assert new_names.get_name_string(name_id) is None


def test_lookup(used_names, name_string_list):
    """Test if lookup returns the expected list of index."""
    name_string_list.append("Tom")
    assert used_names.lookup(name_string_list) == [0, 1, 2, 3]


@pytest.mark.parametrize("expected_ids, name_strs", [
    (0, "Alice"),
    (1, "Bob"),
    (2, "Eve"),
    (None, "James")
])
def test_query(used_names, name_strs, expected_ids):
    """Test if lookup returns the expected index."""
    assert used_names.query(name_strs) == expected_ids
