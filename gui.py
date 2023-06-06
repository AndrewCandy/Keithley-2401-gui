from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import json

# Create a tkinter window to add things to
root = Tk()
root.title("Keithley 2401 GUI")

# Define variables
source_voltage = DoubleVar(root)
source_delay = DoubleVar(root)
source_voltage_start = DoubleVar(root)
source_voltage_stop = DoubleVar(root)
source_voltage_step = DoubleVar(root)
log_num_steps = DoubleVar(root)
trig_count = DoubleVar(root)
current_compliance = DoubleVar(root)
is_up_down = BooleanVar(root)

# Define lists of accepted inputs for string variables
rangenames = ('BEST', 'WORST')
modenames = ('SWE', 'OTHER')
spacenames = ('LIN', 'LOG')
rnames = StringVar(root, value=rangenames)
mnames = StringVar(root, value=modenames)
snames = StringVar(root, value=spacenames)

# Create frame structure to place widgets in
c = ttk.Frame(root, padding=(5, 5, 12, 0))
c.grid(column=0, row=0, sticky=(N,W,E,S))
root.grid_columnconfigure(0, weight=1)
root.grid_rowconfigure(0,weight=1)

# Create option lists for non-numeric inputs
sweep_range_label = Label(c, text='Sweep Range:')
src_sweep_range_lbox = Listbox(c, listvariable=rnames, height=3, selectmode=SINGLE, exportselection=False)
voltage_mode_label = Label(c, text='Voltage Mode:')
src_voltage_mode_lbox = Listbox(c, listvariable=mnames, height=3, selectmode=SINGLE, exportselection=False)
sweep_space_label = Label(c, text='Sweep Space:')
src_sweep_space_lbox = Listbox(c, listvariable=snames, height=3, selectmode=SINGLE, exportselection=False)

# Create sliders and text entry points for numeric inputs
src_voltage_label = Label(c, text='Source Voltage:')
src_voltage_scale = Scale(c, variable=source_voltage, orient="horizontal",
                              from_=0.0, to=10.0, resolution=0.00001, showvalue=0, 
                              tickinterval=2)
src_voltage_entry = Entry(c, textvariable=source_voltage)

src_delay_label = Label(c, text='Source delay:')
src_delay_scale = Scale(c, variable=source_delay, orient="horizontal",
                              from_=0.0, to=1.0, resolution=0.00001, showvalue=0, 
                              tickinterval=2)
src_delay_entry = Entry(c, textvariable=source_delay)

src_voltage_start_label = Label(c, text='Source Voltage Start:')
src_voltage_start_scale = Scale(c, variable=source_voltage_start, orient="horizontal",
                              from_=0.0, to=10.0, resolution=0.00001, showvalue=0, 
                              tickinterval=2)
src_voltage_start_entry = Entry(c, textvariable=source_voltage_start)

src_voltage_stop_label = Label(c, text='Source Voltage Stop:')
src_voltage_stop_scale = Scale(c, variable=source_voltage_stop, orient="horizontal",
                              from_=0.0, to=10.0, resolution=0.00001, showvalue=0, 
                              tickinterval=2)
src_voltage_stop_entry = Entry(c, textvariable=source_voltage_stop)

src_voltage_step_label = Label(c, text='Source Voltage Step:')
src_voltage_step_scale = Scale(c, variable=source_voltage_step, orient="horizontal",
                              from_=0.0, to=1.0, resolution=0.00001, showvalue=0, 
                              tickinterval=.5)
src_voltage_step_entry = Entry(c, textvariable=source_voltage_step)

log_num_steps_label = Label(c, text='Number of Steps:')
log_num_steps_scale = Scale(c, variable=log_num_steps, orient="horizontal",
                              from_=1.0, to=100.0, resolution=0.00001, showvalue=0, 
                              tickinterval=25)
log_num_steps_entry = Entry(c, textvariable=log_num_steps)

trig_count_label = Label(c, text='Trig Count:')
trig_count_scale = Scale(c, variable=trig_count, orient="horizontal",
                              from_=1.0, to=100.0, resolution=0.00001, showvalue=0, 
                              tickinterval=25)
trig_count_entry = Entry(c, textvariable=trig_count)

current_compliance_label = Label(c, text='Current Compliance:')
current_compliance_scale = Scale(c, variable=current_compliance, orient="horizontal",
                              from_=0.0, to=1.0, resolution=0.00001, showvalue=0, 
                              tickinterval=.5)
current_compliance_entry = Entry(c, textvariable=current_compliance)

stairs_button_label = Label(c, text="Stairs up and down?")
stairs_button = Checkbutton(c, variable=is_up_down, width=20)

# Function for when run button is pressed
def setValues():
    '''
    Reads all values from GUI, saves all values to json file if filled out
    or informs user information is missing
    '''
    # Check to see if any boxes are empty (should be impossible)
    if (len(src_sweep_range_lbox.curselection()) != 1 or
        len(src_voltage_mode_lbox.curselection()) != 1 or
        len(src_sweep_space_lbox.curselection()) != 1):
        messagebox.showwarning("Warning!", "You have not selected an option for all parameters.")
    else: # Take all the data and put it in a json file to be used as the new starting value next time the program is run
        dictionary = {
            "source_voltage" : source_voltage.get(),
            "source_delay" : source_delay.get(),
            "source_voltage_start" : source_voltage_start.get(),
            "source_voltage_stop" : source_voltage_stop.get(),
            "source_voltage_step" : source_voltage_step.get(),
            "log_num_steps" : log_num_steps.get(),
            "trig_count" : trig_count.get(),
            "current_compliance" : current_compliance.get(),
            "is_up_down" : is_up_down.get(),
            "source_sweep_range" : rangenames[src_sweep_range_lbox.curselection()[0]],
            "source_voltage_mode" : modenames[src_voltage_mode_lbox.curselection()[0]],
            "source_sweep_space" : spacenames[src_sweep_space_lbox.curselection()[0]],
            "sweep_range_index" : src_sweep_range_lbox.curselection()[0],
            "voltage_mode_index" : src_voltage_mode_lbox.curselection()[0],
            "sweep_space_index" : src_sweep_space_lbox.curselection()[0]
        }
        with open("values.json", "w") as outfile:
            json.dump(dictionary, outfile)

        root.destroy()

button = Button(c, text='Run', command=setValues)

# Place items in GUI
sweep_range_label.grid(column=0, row=0)
src_sweep_range_lbox.grid(column=0, row=1, rowspan=6, sticky=(N,S,E,W))
voltage_mode_label.grid(column=1, row=0)
src_voltage_mode_lbox.grid(column=1, row=1, rowspan=6, sticky=(N,S,E,W))
sweep_space_label.grid(column=2, row=0)
src_sweep_space_lbox.grid(column=2, row=1, rowspan=6, sticky=(N,S,E,W))

src_voltage_label.grid(column=3, columnspan=2, row=1, padx=10)
src_voltage_entry.grid(column=3, columnspan=2, row=2, padx=10, pady=5)
src_voltage_scale.grid(column=3, columnspan=2, row=3, padx=10, pady=0)

src_delay_label.grid(column=3, columnspan=2, row=4, padx=10)
src_delay_entry.grid(column=3, columnspan=2, row=5, padx=10, pady=5)
src_delay_scale.grid(column=3, columnspan=2, row=6, padx=10, pady=0)

src_voltage_start_label.grid(column=0, columnspan=1, row=7, padx=10)
src_voltage_start_entry.grid(column=0, columnspan=1, row=8, padx=10)
src_voltage_start_scale.grid(column=0, columnspan=1, row=9, padx=10)

src_voltage_stop_label.grid(column=1, columnspan=1, row=7, padx=10)
src_voltage_stop_entry.grid(column=1, columnspan=1, row=8, padx=10)
src_voltage_stop_scale.grid(column=1, columnspan=1, row=9, padx=10)

trig_count_label.grid(column=3, columnspan=2, row=7, padx=10)
trig_count_entry.grid(column=3, columnspan=2, row=8, padx=10, pady=5)
trig_count_scale.grid(column=3, columnspan=2, row=9, padx=10, pady=0)

current_compliance_label.grid(column=5, columnspan=2, row=1, padx=10)
current_compliance_entry.grid(column=5, columnspan=2, row=2, padx=10, pady=5)
current_compliance_scale.grid(column=5, columnspan=2, row=3, padx=10, pady=0)

stairs_button_label.grid(column=5, row=5)
stairs_button.grid(column=5, row=6)

button.grid(column=5, columnspan=2, row=9)

# Shade listboxes for easier reading
for i in range(0,len(rangenames),2):
    src_sweep_range_lbox.itemconfigure(i, background='#f0f0ff')

for i in range(0,len(modenames),2):
    src_voltage_mode_lbox.itemconfigure(i, background='#f0f0ff')

for i in range(0,len(spacenames),2):
    src_sweep_space_lbox.itemconfigure(i, background='#f0f0ff')

def sweepSpaceChange(*args):
    if spacenames[src_sweep_space_lbox.curselection()[0]] == 'LOG':
        src_voltage_step_entry.grid_forget()
        src_voltage_step_label.grid_forget()
        src_voltage_step_scale.grid_forget()
        log_num_steps_label.grid(column=2, columnspan=1, row=7, padx=10)
        log_num_steps_entry.grid(column=2, columnspan=1, row=8, padx=10)
        log_num_steps_scale.grid(column=2, columnspan=1, row=9, padx=10)

    else:
        log_num_steps_entry.grid_forget()
        log_num_steps_label.grid_forget()
        log_num_steps_scale.grid_forget()
        src_voltage_step_label.grid(column=2, columnspan=1, row=7, padx=10)
        src_voltage_step_entry.grid(column=2, columnspan=1, row=8, padx=10)
        src_voltage_step_scale.grid(column=2, columnspan=1, row=9, padx=10)


# Trigger a function every time sweep space choice is changed
src_sweep_space_lbox.bind('<<ListboxSelect>>', sweepSpaceChange)


# Set starting values
with open('values.json', 'r') as openfile:
    saved_vals = json.load(openfile)

source_voltage.set(saved_vals["source_voltage"])
source_delay.set(saved_vals["source_delay"])
source_voltage_start.set(saved_vals["source_voltage_start"])
source_voltage_stop.set(saved_vals["source_voltage_stop"])
source_voltage_step.set(saved_vals["source_voltage_step"])
log_num_steps.set(saved_vals["log_num_steps"])
trig_count.set(saved_vals["trig_count"])
current_compliance.set(saved_vals["current_compliance"])
is_up_down.set(saved_vals["is_up_down"])
src_sweep_range_lbox.selection_set(saved_vals["sweep_range_index"])
src_voltage_mode_lbox.selection_set(saved_vals["voltage_mode_index"])
src_sweep_space_lbox.selection_set(saved_vals["sweep_space_index"])

# Run sweepSpaceChange once to populate blank space
sweepSpaceChange()

root.mainloop()