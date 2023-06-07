"""Test the guiint module."""
import pytest
from unittest.mock import Mock

from names import Names
from devices import Devices
from network import Network
from monitors import Monitors
from scanner import Scanner
from guiint import GuiInterface
from parse import Parser

"""
Methods to test:
----------------
list_of_switches(self): returns list of switch names (strings)
list_of_outputs(self): returns list of output names (strings)
get_switch_state(self, switch_name): returns state of switch (boolean)
set_switch_state(self, switch_name, switch_state): sets switch state
get_output_state(self, output_name): returns state of monitor (bool 0 if unmonitored)
set_output_state(self, output_name, output_state): add or remove monitor
run_network(self, n_cycles): resets and runs the network for n-cycles
continue_network(self, n_cycles): continues running the network for n-cycles
get_signals(self): returns dictionary of all monitered signal states for each monitored output
"""


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
    """Return a new scanner instance for the first test file."""
    return Scanner("test_misc_files/file_for_test_guiint.txt", new_names)


@pytest.fixture
def new_parser(new_names, new_devices, new_network, new_monitors, new_scanner):
    """Return a new parser instance."""
    return Parser(new_names, new_devices, new_network,
                  new_monitors, new_scanner)


@pytest.fixture
def new_guiint(new_names, new_devices, new_network,
               new_monitors, new_scanner, new_parser):
    """Return a new guiint instance."""
    new_parser.parse_network()
    return GuiInterface(new_names, new_devices, new_network,
                        new_monitors, new_scanner)


def test_get_list_of_switches(new_guiint):
    """Test that the correct list of switches is returned."""
    assert sorted(new_guiint.list_of_switches()
                  ) == sorted(['switch1', 'switch2'])


def test_get_list_of_outputs(new_guiint):
    """Test that the correct list of outputs is returned."""
    assert sorted(new_guiint.list_of_outputs()) == sorted(
        ['switch1', 'switch2', 'or1'])


def test_get_switch_state(new_guiint):
    """Test that the correct switch state is returned."""
    assert new_guiint.get_switch_state('switch1') == 1
    assert new_guiint.get_switch_state('switch2') == 0


def test_set_switch_state(new_guiint):
    """Test that the correct switch state is set."""
    new_guiint.set_switch_state('switch1', 0)
    new_guiint.set_switch_state('switch2', 1)

    # Check actual state changes - not just the return value
    switch_1_id = new_guiint.names.query('switch1')
    switch_2_id = new_guiint.names.query('switch2')
    switch_1_device = new_guiint.devices.get_device(switch_1_id)
    switch_2_device = new_guiint.devices.get_device(switch_2_id)

    assert switch_1_device.switch_state == 0
    assert switch_2_device.switch_state == 1


def test_get_output_state(new_guiint):
    """Test that the correct output state is returned."""
    assert new_guiint.get_output_state('switch1') == 0
    assert new_guiint.get_output_state('switch2') == 0
    assert new_guiint.get_output_state('or1') == 1


def test_set_output_state(new_guiint):
    """Test that the correct output state is set."""
    # Flip the monitoring status of all the devices
    new_guiint.set_output_state('switch1', 1)
    new_guiint.set_output_state('switch2', 1)
    new_guiint.set_output_state('or1', 0)

    or_1_id = new_guiint.names.query('or1')
    switch_1_id = new_guiint.names.query('switch1')
    switch_2_id = new_guiint.names.query('switch2')

    # Check that the monitors dictionary has been updated
    assert not (or_1_id, None) in new_guiint.monitors.monitors_dictionary
    assert (switch_1_id, None) in new_guiint.monitors.monitors_dictionary
    assert (switch_2_id, None) in new_guiint.monitors.monitors_dictionary


def test_run_network(new_guiint):
    """Test that the network restarts and runs correctly."""
    new_guiint.devices.cold_startup = Mock()
    new_guiint.monitors.reset_monitors = Mock()
    new_guiint.network.execute_network = Mock()
    new_guiint.monitors.record_signals = Mock()

    new_guiint.run_network(10)

    assert new_guiint.devices.cold_startup.call_count == 1
    assert new_guiint.monitors.reset_monitors.call_count == 1
    assert new_guiint.network.execute_network.call_count == 10
    assert new_guiint.monitors.record_signals.call_count == 10


def test_continue_network(new_guiint):
    """Test that the network continues correctly."""
    new_guiint.network.execute_network = Mock()
    new_guiint.monitors.record_signals = Mock()
    new_guiint.continue_network(10)

    assert new_guiint.network.execute_network.call_count == 10
    assert new_guiint.monitors.record_signals.call_count == 10


def test_get_signals(new_guiint):
    """Test that the correct signals are returned. - integrates a few of
    the other methods"""

    # Check that the monitored signals are empty to start with
    assert new_guiint.get_signals() == {'or1': []}

    new_guiint.continue_network(1)

    # Check that the monitored signals update as expected
    assert new_guiint.get_signals() == {'or1': [1]}

    new_guiint.set_switch_state('switch1', 0)
    new_guiint.continue_network(1)
    assert new_guiint.get_signals() == {'or1': [1, 0]}

    # Check that the monitored signals are empty again after the monitor is
    # removed
    new_guiint.set_output_state('or1', 0)
    new_guiint.continue_network(1)
    assert new_guiint.get_signals() == {}
