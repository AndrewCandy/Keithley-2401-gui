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
        """
        Initializes the Test class
        """
        self.selected_devices = grid_to_list(grid)
        self.start_time = dt.now()
        self.chiplet_name = chiplet_name
        self.test_num = test_num

    def set_start_time(self):
        """
        Sets the test start time to the current time
        To be called
        return: none
        """
        self.start_time = dt.now()

    @abstractmethod
    def run_sourcemeter(self, instrument):
        """
        Sends appropriate commands to the sourcemeter for the given test
        return:
            String of data from sourcemeter
        """

    @abstractmethod
    def get_test_type(self):
        """
        returns a string describing the type of test being run
        """

    @abstractmethod
    def get_test_parameters(self):
        """
        returns a array describing the parameteres used in the test being run
        """


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

    def __init__(
        self,
        grid,
        test_num,
        chiplet_name,
        space,
        source_voltage,
        source_delay,
        source_voltage_start,
        source_voltage_stop,
        source_voltage_neg,
        num_steps,
        neg_steps,
        current_compliance,
        cycles,
        accuracy
    ):
        """
        Initailizes the the IV_Test class and parent Test class
        """
        super().__init__(grid, test_num, chiplet_name)
        self._space = space
        self._source_voltage = source_voltage
        self._source_delay = source_delay
        self._source_voltage_start = source_voltage_start
        self._source_voltage_stop = source_voltage_stop
        self._source_voltage_neg = source_voltage_neg
        self._num_steps = num_steps
        self._neg_steps = neg_steps
        self._trigger_count = num_steps
        self._trigger_count_neg = neg_steps
        self._current_compliance = current_compliance
        self._cycles = cycles
        self._accuracy = accuracy

    def get_voltage_space(self):
        """
        returns LIN or LOG based on what type of test is selected
        """
        return self._space

    def run_sourcemeter(self, instrument):
        """
        Determine what version of IV test to run and call respective function from functions.py
        return:
            A string of vlaues from the test
        """
        measurements = ""
        if self._space == "LIN":
            voltage_step = calc_voltage_step(
                self._source_voltage_start, self._source_voltage_stop, self._num_steps
            )
            neg_voltage_step = calc_voltage_step(
                self._source_voltage_start, self._source_voltage_neg, self._neg_steps
            )
            for _ in range(0, self._cycles):
                measurements += (
                    functions.staircase_lin(
                        instrument=instrument,
                        current_compliance=self._current_compliance,
                        source_voltage=self._source_voltage,
                        source_delay=self._source_delay,
                        source_voltage_start=self._source_voltage_start,
                        source_voltage_stop=self._source_voltage_stop,
                        source_voltage_step=voltage_step,
                        source_voltage_neg =self._source_voltage_neg,
                        neg_step=neg_voltage_step,
                        trig_count=self._trigger_count,
                        trig_count_neg = self._trigger_count_neg,
                        accuracy = self._accuracy
                    )
                    + ","
                )
        elif self._space == "LOG":
            measurements += functions.staircase_log(
                instrument=instrument,
                current_compliance=self._current_compliance,
                source_voltage=self._source_voltage,
                source_delay=self._source_delay,
                source_voltage_start=self._source_voltage_start,
                source_voltage_stop=self._source_voltage_stop,
                log_num_steps=self._num_steps,
                trig_count=self._trigger_count,
            )
        return measurements.rstrip(",")

    def get_test_type(self):
        """
        returns a string describing the type of test being run
        """
        test_type = ""
        if self._space == "LIN":
            test_type += "Linear_"
        elif self._space == "LOG":
            test_type += "Logarithmic_"
        # Show it was an IV
        test_type += f"IV_{self.test_num}"
        return test_type
    def get_test_parameters(self):
        parameters = []
        parameters.append(self._space)#0
        parameters.append(self._source_voltage_start)#1
        parameters.append(self._source_voltage_stop)#2
        parameters.append(self._source_voltage_neg)#3
        parameters.append(None)#Set Voltage  4
        parameters.append(None)#Reset Voltage  5
        parameters.append(None)#Read Voltage  6
        parameters.append(self._num_steps)#7
        parameters.append(self._neg_steps)#8
        parameters.append(self._source_delay)#9
        parameters.append(self._accuracy)#10
        parameters.append(self._current_compliance)#11
        parameters.append(self._cycles)#12
        return parameters


class FormingTest(Test):
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
    """

    def __init__(
        self,
        grid,
        test_num,
        chiplet_name,
        space,
        source_voltage,
        source_delay,
        source_voltage_start,
        source_voltage_stop,
        num_steps,
        current_compliance,
        cycles,
        accuracy
    ):
        """
        Initailizes the the IV_Test class and parent Test class
        """
        super().__init__(grid, test_num, chiplet_name)
        self._space = space
        self._source_voltage = source_voltage
        self._source_delay = source_delay
        self._source_voltage_start = source_voltage_start
        self._source_voltage_stop = source_voltage_stop
        self._num_steps = num_steps
        self._trigger_count = num_steps
        self._current_compliance = current_compliance
        self._cycles = cycles
        self._accuracy = accuracy

    def get_voltage_space(self):
        """
        returns LIN or LOG based on what type of test is selected
        """
        return self._space

    def run_sourcemeter(self, instrument):
        """
        Determine what version of IV test to run and call respective function from functions.py
        return:
            A string of vlaues from the test
        """
        measurements = ""
        if self._space == "LIN":
            voltage_step = calc_voltage_step(
                self._source_voltage_start, self._source_voltage_stop, self._num_steps
            )
            for _ in range(0, self._cycles):
                measurements += (
                    functions.staircase_forming(
                        instrument=instrument,
                        current_compliance=self._current_compliance,
                        source_voltage=self._source_voltage,
                        source_delay=self._source_delay,
                        source_voltage_start=self._source_voltage_start,
                        source_voltage_stop=self._source_voltage_stop,
                        source_voltage_step=voltage_step,
                        trig_count=self._trigger_count,
                        accuracy = self._accuracy
                    )
                    + ","
                )
        elif self._space == "LOG":
            measurements += functions.staircase_log(
                instrument=instrument,
                current_compliance=self._current_compliance,
                source_voltage=self._source_voltage,
                source_delay=self._source_delay,
                source_voltage_start=self._source_voltage_start,
                source_voltage_stop=self._source_voltage_stop,
                log_num_steps=self._num_steps,
                trig_count=self._trigger_count,
            )
        return measurements.rstrip(",")

    def get_test_type(self):
        """
        returns a string describing the type of test being run
        """
        test_type = ""
        if self._space == "LIN":
            test_type += "Linear_"
        elif self._space == "LOG":
            test_type += "Logarithmic_"
        # Show it was an IV
        test_type += f"Forming_{self.test_num}"
        return test_type
    def get_test_parameters(self):
        parameters = []
        parameters.append(self._space)#0
        parameters.append(self._source_voltage_start)#1
        parameters.append(self._source_voltage_stop)#2
        parameters.append(None)#Neg Voltage  3
        parameters.append(None)#Set Voltage  4
        parameters.append(None)#Reset Voltage  5
        parameters.append(None)#Read Voltage  6
        parameters.append(self._num_steps)#7
        parameters.append(None)#Neg Steps  8
        parameters.append(self._source_delay)#9
        parameters.append(self._accuracy)#10
        parameters.append(self._current_compliance)#11
        parameters.append(self._cycles)#12
        return parameters
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

    def __init__(
        self,
        grid,
        test_num,
        chiplet_name,
        source_voltage,
        source_delay,
        current_compliance,
        cycles,
        set_voltage,
        read_voltage,
        reset_voltage,
        accuracy
    ):
        """
        Initailizes the the EnduranceTest class and parent Test class
        """
        super().__init__(grid, test_num, chiplet_name)
        self._set_voltage = set_voltage
        self._read_voltage = read_voltage
        self._reset_voltage = reset_voltage
        self._cycles = cycles
        self._current_compliance = current_compliance
        self._source_voltage = source_voltage
        self._source_delay = source_delay
        self._accuracy = accuracy

    def run_sourcemeter(self, instrument):
        """
        Call respective test function from functions.py
        """
        measurements = ""
        voltage_list = functions.create_voltage_list(
            set_voltage=self._set_voltage,
            read_voltage=self._read_voltage,
            reset_voltage=self._reset_voltage,
        )
        for _ in range(0, self._cycles, 5):
            measurements += (
                functions.endurance_test(
                    instrument=instrument,
                    accuracy=self._accuracy,
                    current_compliance=self._current_compliance,
                    source_voltage=self._source_voltage,
                    source_delay=self._source_delay,
                    voltage_list=voltage_list,
                    list_length=40,
                )
                + ","
            )
        return measurements.rstrip(",")

    def get_test_type(self):
        """
        returns a string describing the type of test being run
        """
        return f"Endurance_{self.test_num}"
    
    def get_test_parameters(self):
        parameters = [] 
        parameters.append('Endurance')#0
        parameters.append(None)#Start Voltage IV 1
        parameters.append(None)#Stop Voltage IV 2
        parameters.append(None)#Neg. Voltage IV 3 
        parameters.append(self._set_voltage)#Set Voltage  4
        parameters.append(self._reset_voltage)#Reset Voltage  5
        parameters.append(self._read_voltage)#Read Voltage  6
        parameters.append(40)#7
        parameters.append(None)#Neg Steps IV8
        parameters.append(self._source_delay)#9
        parameters.append(self._accuracy)#10
        parameters.append(self._current_compliance)#11
        parameters.append(self._cycles)#12
        return parameters


class ReadTest(Test):
    """
    Class containing all information and functions specific to Endurance tests

    Attributes:
        _read_voltage:
        _cycles:
        _current_compliance:
        _source_voltage:
        _source_delay:
    """

    def __init__(
        self,
        grid,
        test_num,
        chiplet_name,
        source_voltage,
        source_delay,
        current_compliance,
        cycles,
        read_voltage,
        accuracy
    ):
        """
        Initailizes the the EnduranceTest class and parent Test class
        """
        super().__init__(grid, test_num, chiplet_name)
        self._accuracy = accuracy
        self._read_voltage = read_voltage
        self._cycles = cycles
        self._current_compliance = current_compliance
        self._source_voltage = source_voltage
        self._source_delay = source_delay

    def run_sourcemeter(self, instrument):
        """
        Call respective test function from functions.py
        """
        measurements = ""
        voltage_list = functions.create_read_voltage_list(
            read_voltage=self._read_voltage
        )
        for _ in range(0, self._cycles):
            measurements += (
                functions.read_test(
                    instrument=instrument,
                    accuracy = self._accuracy,
                    current_compliance=self._current_compliance,
                    source_voltage=self._source_voltage,
                    source_delay=self._source_delay,
                    voltage_list=voltage_list,
                    list_length=2,
                )
                + ","
            )
        return measurements.rstrip(",")

    def get_test_type(self):
        """
        returns a string describing the type of test being run
        """
        return f"Read_{self.test_num}"

    def get_test_parameters(self):
        parameters = []
        parameters.append("Read Endurance")#0
        parameters.append(None)#Start Voltage IV 1
        parameters.append(None)#Stop Voltage IV 2
        parameters.append(None)#Neg. Voltage IV 3
        parameters.append(None)#Set Voltage  4
        parameters.append(None)#Reset Voltage  5
        parameters.append(self._read_voltage)#Read Voltage  6
        parameters.append(2)#7
        parameters.append(None)#Neg Steps IV8
        parameters.append(self._source_delay)#9
        parameters.append(self._accuracy)#10
        parameters.append(self._current_compliance)#11
        parameters.append(self._cycles)#12
        return parameters

def calc_voltage_step(voltage_start, voltage_stop, num_steps):
    """
    Return:
        The step size for the requested number of steps to occur
        between start and stop voltages
    """
    voltage_step = (voltage_stop - voltage_start) / num_steps
    return voltage_step


def grid_to_list(grid):
    """
    Take square device grid and convert it to a list of (x,y) namedtuples
    return:
        A list of named tuples containing xy coords
    """
    Point = namedtuple("Point", "x y")
    tuple_list = []
    for col, column in enumerate(grid):
        for row, cell in enumerate(column):
            if cell == 1:
                point = Point(col+1, row+1)
                tuple_list.append(point)
    return tuple_list
