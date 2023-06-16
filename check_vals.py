# def check_source_voltage(*args):
#     '''
#     '''
#     sv = source_voltage.get()
#     if sv > source_voltage_minmax[1]:
#         source_voltage.set(source_voltage_minmax[1])
#     elif sv < source_voltage_minmax[0]:
#         source_voltage.set(source_voltage_minmax[0])
#     elif (spacename == 'LOG' and sv == source_voltage_minmax[0]):
#         source_voltage.set(source_voltage_minmax[0] + 0.00001)
# def check_source_delay(*args):
#     '''
#     '''
#     sd = source_delay.get()
#     if sd > source_delay_minmax[1]:
#         source_delay.set(source_delay_minmax[1])
#     elif sd <= source_delay_minmax[0]:
#         source_delay.set(source_delay_minmax[0])
# def check_voltage_start(*args):
#     '''
#     '''
#     svs = source_voltage_start.get()
#     if svs > source_voltage_minmax[1]:
#         source_voltage_start.set(source_voltage_minmax[1])
#     elif svs < source_voltage_minmax[0]:
#         source_voltage_start.set(source_voltage_minmax[0])
#     elif (spacename == 'LOG' and svs == source_voltage_minmax[0]):
#         source_voltage_start.set(source_voltage_minmax[0] + 0.00001)
# def check_voltage_stop(*args):
#     '''
#     '''
#     svs = source_voltage_stop.get()
#     if svs > source_voltage_minmax[1]:
#         source_voltage_stop.set(source_voltage_minmax[1])
#     elif svs < source_voltage_minmax[0]:
#         source_voltage_stop.set(source_voltage_minmax[0])
#     elif (spacename == 'LOG' and svs == source_voltage_minmax[0]):
#         source_voltage_stop.set(source_voltage_minmax[0] + 0.00001)
# def check_num_steps(*args):
#     '''
#     '''
#     ns = num_steps.get()
#     if ns > num_steps_minmax[1]:
#         num_steps.set(num_steps_minmax[1])
#     elif ns < num_steps_minmax[0]:
#         num_steps.set(num_steps_minmax[0])
# def check_current(*args):
#     '''
#     '''
#     cc = current_compliance.get()
#     if cc > current_minmax[1]:
#         current_compliance.set(current_minmax[1])
#     elif cc < current_minmax[0]:
#         current_compliance.set(current_minmax[0])
#     elif (spacename == 'LOG' and cc == current_minmax[0]):
#         current_compliance.set(current_minmax[0] + 0.00001)
# call value check functions whenever a value in the GUI changes
# source_voltage.trace_add('write', check_source_voltage)
# source_delay.trace_add('write', check_source_delay)
# source_voltage_start.trace_add('write', check_voltage_start) # Turns out this is really annoying for entering values into the gui
# source_voltage_stop.trace_add('write', check_voltage_stop)
# num_steps.trace_add('write', check_num_steps)
# current_compliance.trace_add('write', check_current)
