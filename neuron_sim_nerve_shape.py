import misc_functions as mf
import plot as pt
import threshold as th
from neuron import h
import numpy as np
from Axon_Models import hh_cable_geometry
from Axon_Models import simple_cable_geometry
from Axon_Models import mrg_cable_geometry
from Axon_Models import mrg_parameters as ap
import sys
sys.path.insert(0, "C:/nrn/lib/python")
import neuron


class NeuronSimNerveShape:

    def __init__(self, nerve_shape, time_axis, stimulus, total_time):
        super(NeuronSimNerveShape, self).__init__()

        h.load_file('stdrun.hoc')
        h.celsius = 37
        h.dt = 0.001  # ms

        self.axon = self.generate_axon(nerve_shape)


    def generate_axon(self, nerve_shape):
       if mp.axon_type == 'HH':
           axon = self.hh(mp.diameter, mp.x, mp.y, mp.z, mp.angle, mp.length)
       elif mp.axon_type == 'RMG':
           axon = self.mrg(mp.diameter, mp.x, mp.y, mp.z, mp.angle, mp.length)
       else:
           axon = self.simple(mp.diameter, mp.x, mp.y, mp.z, mp.angle, mp.length)

       mf.record_membrane_potentials(axon, 0.5)

       return axon


    def simple(self, diameter, x, y, z, angle, length):
        segments = 1

        node_diameter = 0.3449 * diameter - 0.1484  # um; the formula is from Olivar Izard Master's thesis
        internode_diameter = diameter
        node_length = 1
        if diameter > 4:
            internode_length = 969.3 * np.log(diameter) - 1144.6
        else:
            internode_length = 100 * diameter
        axons_number = 1
        amount = int((length / (node_length + internode_length)) / axons_number)
        node_internode_pairs_per_unit_vector = amount
        phi = [angle / 360 * 2 * np.pi]
        theta = [90 / 360 * 2 * np.pi, 90 / 360 * 2 * np.pi]
        # phi = [np.pi / 2, np.pi / 2]

        simple_model = simple_cable_geometry.BendedAxon(theta, phi, axons_number, x, y, z, segments,
                                                        internode_diameter,
                                                        node_diameter, node_length, internode_length,
                                                        node_internode_pairs_per_unit_vector)

        return simple_model
