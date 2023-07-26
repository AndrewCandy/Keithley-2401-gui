# Controller module for sourcemeter GUI

This module serves as the controller for interacting with the source meter, microcontroller, and GUI.

## Project Structure

The project is structured as follows:

- `source_meter.py`: The main controller module that manages the interaction between the source meter, microcontroller, and GUI.

- `functions.py`: A module containing various utility functions used by the controller.

- `gui.py`: The graphical user interface module for the project.

- `microserial.py`: A module for serial communication with the microcontroller.

- `post_test_gui.py`: A module for displaying post-test results GUI.

- `tests.py`: A module containing different test classes.

- `README.md`: This readme file providing an overview of the project.

## Installation

To run this project, please follow these steps:

1. Clone the repository:

   ```
   git clone https://github.com/AndrewCandy/Keithley-2401-gui
   ```

2. Install the required dependencies:

    numpy 
    pandas 
    pyvisa 
    You can install these dependencies by using pip and the following command:

    pip install numpy pandas pyvisa

3. Run the `source_meter.py` file:
    You cannot run the file if the sourcemeter is not plugged in via a GPIB will create an error

## Usage

1. Instantiate the `SourceMeter` class from the `controller` module:

   ```python
   sm = SourceMeter()
   ```

2. Run the desired tests by calling the `run_test()` method:

   ```python
   sm.run_test()
   ```

3. Generate excel sheets containing test data and statistics by calling the `create_excel_sheets()` method:

   ```python
   sm.create_excel_sheets()
   ```

4. View post-test results using the `run_post_test_gui()` method:

   ```python
   sm.run_post_test_gui()
   ```


## GUI USAGE

