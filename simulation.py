'''
@author: Rapp & Braun
'''

import sys
sys.path.insert(0, "C:/nrn/lib/python")

import nerve_widget as ner
import stimulus as stim
import time
import pandas as pd
import e_field_widget as em
import neuron_sim as ns
from matplotlib import pyplot as plt


# 1)
# field parameters
# choose field from file (csv or already processed python matrix)
field_offset = 0
e_field_name = 'halsmodell'
# edit field: make sure boundary condition are given

# 2)
# create nerve(s)
number_of_nerves = 1
# for each nerve
number_of_axons = 1
# create list of knicks and corresponding angles
nerve_angle_list = []
dict_axon_types_diameters = {"HH": [], "modHH": [], "RMG": []}
nerve_length = 60000
# create_nerve()

# 3)
# position nerve(s) in field
nerve_position = [3000, 60, 50500]
# nerve position editable via sliders
# interactively show nerve in field + e_field_along_axon (must be calculated immediately)

# 4)
# unity stimulus: shape

# 5)
# Start neuron, start simulation




e_field_list = em.get_e_field(e_field_name)

if e_field_name == 'biovoxel':
    phrenic_nerve = ner.Nerve(3000, 60, 50500, 60000, 550, 'N. phrenicus')
    vagus_nerve = ner.Nerve(8000, 0, 54000, 60000, 2300, 'N.Vagus')

#if e_field_name == 'halsmodell':
else:
    phrenic_nerve = ner.Nerve(x=514, y=-40000, z=27542, length=80000, nerv_diam=550, name='N. phrenicus')
    vagus_nerve = ner.Nerve(5155, -40000, 30949, 80000, 2300, 'N.Vagus')
    # Position (Mittelpunkt) vom Phrenic nerve: P(x, z)=P(0.514 , 27.542)
    # vom Vagus nerve: V(x,z)= V(5.155 , 30.949)
    # Beide Nerven verlaufen von y=-18 bis y=27

# define axon bending in neuron sim
# define nerve properties in nerve
# change e_x or e_y in quasi_potentials (due to CST bug)

# ===============================================================================
# stimulus settings
# ==============================================================================
print('Start scanning field')
total_time = 20
pulse_amp = 1800
time_axis, stimulus_th, name = stim.get_cosine(total_time, 1, 0.1, 1)
stimulus = stimulus_th * pulse_amp

interpolation_radius_index = 2  # adapt to e-field resolution

phrenicus_dict = {}
phrenicus_dict['x'] = []
phrenicus_dict['z'] = []
phrenicus_dict['threshold'] = []
phrenicus_dict['name'] = []
for axon_info in phrenic_nerve.axon_infos_list:
    neuron_sim = ns.NeuronSim(axon_info, e_field_list, time_axis, stimulus, total_time)
    neuron_sim.quasipot(interpolation_radius_index)
    neuron_sim.simple_simulation()
#     th = neuron_sim.threshold_simulation(stimulus_th)
#     print(th)
#     phrenicus_dict['x'].append(axon_info.x)
#     phrenicus_dict['z'].append(axon_info.z)
#     phrenicus_dict['threshold'].append(th)
#     phrenicus_dict['name'].append(neuron_sim.axon.name)
#     print(th)
#
# df = pd.DataFrame(phrenicus_dict)
# df.to_csv('Phrenicus_simple_cosine' + '.csv',
#     index=False)

# ===============================================================================
# Visualization:
# ===============================================================================

# plotter = field_plot.FieldPlot(storage, e_field_matrix_list[3])
# plotter.subplot_efield_potential_driving_function(phrenic_nerve, phrenic_nerve.name)
# plotter.subplot_efield_potential_driving_function(vagus_nerve, vagus_nerve.name)
#
# field_plot.plot_2d_field_with_cable(e_field_list[3], phrenic_nerve, 1e3, phrenic_nerve.name)
# plotter.plot_2d_field_with_cable(vagus_nerve, 1e3, vagus_nerve.name)
# plotter.plot_2d_field_with_cable(nerve.axon_list[1], 1e3)
# plotter.plot_2d_field_with_cable(nerve.axon_list[2], 1e3)
# field_plot.plot_2d_field(e_field_list[3])

#===============================================================================
# simulation
#===============================================================================
# start = time.time()
#
# end = time.time()
# print("Simulation time: ", end-start)


#===============================================================================
# plot
#===============================================================================
# for axon, vector in zip(phrenic_nerve.axon_infos_list, ve:
#     # if len(axon.potential_vector_list) > 600:
#     # pt.plot_traces(axon.name, axon.potential_vector_list[0::10], time_axis, stimulus)
#     pt.plot_traces_and_field('Nodes: ' + axon.name, axon.potential_vector_node_list, time_axis, stimulus, axon)
#     print('Last sample of membrane potential', axon.potential_vector_list[0][-1])
#     print('max of membrane potential', max(axon.potential_vector_list[0]))
#     print('max of membrane potential', max(axon.potential_vector_list[-1]))

# for axon in vagus_nerve.axon_list:
#     # if len(axon.potential_vector_list) > 600:
#     # pt.plot_traces(axon.name, axon.potential_vector_list[0::10], time_axis, stimulus)
#     pt.plot_traces_and_field('Nodes: ' + axon.name, axon.potential_vector_node_list, time_axis, stimulus, axon)
#     print('Last sample of membrane potential', axon.potential_vector_list[0][-1])
#     print('max of membrane potential', max(axon.potential_vector_list[0]))
#     print('max of membrane potential', max(axon.potential_vector_list[-1]))

plt.show()
print('Fertig. Danke für die Mitarbeit!')