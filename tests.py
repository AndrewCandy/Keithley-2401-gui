"""
Creates test classes to allow for queueing of variations of the same test type
"""
# Library imports
from abc import ABC, abstractmethod
from datetime import datetime as dt
from collections import namedtuple
import functions


class Test(ABC):
    """
    Create an abstract class to hold test methods

    Attributes:
        grid: Nested list containing device grid config
        start_time: DateTime Object to contain the start time of the test
        chiplet_name: String with no special characters used to id chiplet

    """

    def __init__(self, grid, test_num, chiplet_name):
        '''
        Initializes the Test class
        '''
        self.selected_devices = grid_to_list(grid)
        self.start_time = dt.now()
        self.chiplet_name = chiplet_name
        self.test_num = test_num

    def set_start_time(self):
        '''
        Sets the test start time to the current time
        To be called 
        return: none
        '''
        self.start_time = dt.now()

    @abstractmethod
    def run_sourcemeter(self, instrument):
        '''
        Sends appropriate commands to the sourcemeter for the given test
        return:
            String of data from sourcemeter
        '''

    @abstractmethod
    def get_test_type(self):
        '''
        returns a string describing the type of test being run
        '''


class IVTest(Test):
    """
    Class containing all information and functions specific to IV tests

    Attributes:
        _voltage_range:
        _mode:
        space:
        _source_voltage:
        _source_delay:
        _source_voltage_start:
        _source_voltage_stop:
        _num_steps:
        _current_compliance:
        _is_up_down:
    """

    def __init__(self, grid, test_num, chiplet_name, voltage_range, mode, space,
                 source_voltage, source_delay, source_voltage_start,
                 source_voltage_stop, num_steps, current_compliance, is_up_down
                 ):
        '''
        Initailizes the the IV_Test class and parent Test class
        '''
        super().__init__(grid, test_num, chiplet_name)
        self._range = voltage_range
        self._mode = mode
        self._space = space
        self._source_voltage = source_voltage
        self._source_delay = source_delay
        self._source_voltage_start = source_voltage_start
        self._source_voltage_stop = source_voltage_stop
        self._num_steps = num_steps
        self._trigger_count = num_steps
        self._current_compliance = current_compliance
        self._is_up_down = is_up_down

    def get_voltage_space(self):
        return self._space

    def run_sourcemeter(self, instrument):
        '''
        Determine what version of IV test to run and call respective function from functions.py
        return:
            A string of vlaues from the test
        '''
        measurements = ''
        if self._space == 'LIN':
            voltage_step = calc_voltage_step(
                self._source_voltage_start,
                self._source_voltage_stop,
                self._num_steps
            )
            measurements += functions.staircase_lin(
                instrument=instrument,
                current_compliance=self._current_compliance,
                source_voltage=self._source_voltage,
                source_delay=self._source_delay,
                source_voltage_start=self._source_voltage_start,
                source_voltage_stop=self._source_voltage_stop,
                source_voltage_step=voltage_step,
                trig_count=self._trigger_count
            )
        elif self._space == 'LOG':
            measurements += functions.staircase_log(
                instrument=instrument,
                is_up_down=self._is_up_down,
                current_compliance=self._current_compliance,
                source_voltage=self._source_voltage,
                source_delay=self._source_delay,
                source_voltage_start=self._source_voltage_start,
                source_voltage_stop=self._source_voltage_stop,
                log_num_steps=self._num_steps,
                trig_count=self._trigger_count
            )
        return measurements

    def get_test_type(self):
        '''
        returns a string describing the type of test being run
        '''
        test_type = ""
        if self._space == 'LIN':
            test_type += "Linear_"
        elif self._space == 'LOG':
            test_type += "Logarithmic_"
        # Show it was an IV
        test_type += f"IV_{self.test_num}"
        return test_type


class EnduranceTest(Test):
    """
    Class containing all information and functions specific to Endurance tests

    Attributes:
        _set_voltage:
        _read_voltage:
        _reset_voltage:
        _cycles:
        _current_compliance:
        _source_voltage:
        _source_delay:
    """

    def __init__(self, grid, test_num, chiplet_name, source_voltage, source_delay,
                 current_compliance, cycles, set_voltage, read_voltage,
                 reset_voltage
                 ):
        '''
        Initailizes the the EnduranceTest class and parent Test class
        '''
        super().__init__(grid, test_num, chiplet_name)
        self._set_voltage = set_voltage
        self._read_voltage = read_voltage
        self._reset_voltage = reset_voltage
        self._cycles = cycles
        self._current_compliance = current_compliance
        self._source_voltage = source_voltage
        self._source_delay = source_delay

    def run_sourcemeter(self, instrument):
        '''
        Call respective test function from functions.py
        '''
        measurements = ''
        voltage_list = functions.create_voltage_list(
            set_voltage=self._set_voltage,
            read_voltage=self._read_voltage,
            reset_voltage=self._reset_voltage
        )
        for _ in range(0, self._cycles, 5):
            measurements += functions.endurance_test(
                instrument=instrument,
                current_compliance=self._current_compliance,
                source_voltage=self._source_voltage,
                source_delay=self._source_delay,
                voltage_list=voltage_list,
                list_length=self._cycles*8
            )
        return measurements

    def get_test_type(self):
        '''
        returns a string describing the type of test being run
        '''
        return f"Endurance_{self.test_num}"

# TODO: Add class for set and reset pulses


def calc_voltage_step(voltage_start, voltage_stop, num_steps):
    '''
    Return:
        The step size for the requested number of steps to occur
        between start and stop voltages
    '''
    voltage_step = (voltage_stop - voltage_start) / num_steps
    return voltage_step


def grid_to_list(grid):
    '''
    Take square device grid and convert it to a list of (x,y) namedtuples
    return:
        A list of named tuples containing xy coords
    '''
    Point = namedtuple("Point", "x y")
    tuple_list = []
    for col in range(len(grid)):
        for row in range(len(grid[col])):
            if grid[col][row] == 1:
                point = Point(col, row)
                tuple_list.append(point)
    return tuple_list
