import sys

sys.path.insert(0, "C:/nrn/lib/python")

import numpy as np
import neuron
import nrn


class Axon(object):

    def __init__(self, x=500, y=500, z=500, segments=1, node_diameter=10, node_length=1, number_of_nodes=10):

        self.sections = []
        self.node_length = node_length
        self.internode_length = node_length
        self.name = "HH Axon ," + "Node \u2300 = " + str(node_diameter)

        node = Node(segments, node_length, node_diameter)
        self.sections.append(node)

        for i in range(number_of_nodes-1):
            node = Node(segments, node_length, node_diameter)
            node.connect(self.sections[-1], 1)
            self.sections.append(node)

        self.x = x + self.get_node_locations()
        self.y = y
        self.z = z

    def get_node_locations(self):
        '''
        Returns a list with the absolute locations of the nodes in the axon in um.
        '''
        node_list = []
        length_list = []

        for sec in self.sections:
            normed_nodes = np.asarray(self.get_normalized_nodes(sec))

            if len(length_list) == 0:
                node_list.extend(normed_nodes * sec.L)
                length_list.append(sec.L)
            else:
                node_list.extend(normed_nodes * sec.L + length_list[-1])
                length_list.append(sec.L + length_list[-1])

        return np.asarray(node_list)

    def get_normalized_nodes(self, sec):
        """
        Returns an array of all segment objects.
        """
        return np.asarray([seg.x for seg in sec])

    def get_segments(self):
        """
        Returns a list of all segment objects.
        """
        seg_list = []
        for sec in self.sections:
            seg_list.extend([sec(seg.x) for seg in sec])
        return np.asarray(seg_list)


class SuperCompartment(nrn.Section):

    def __init__(self, segments, length, diameter):
        super(SuperCompartment, self).__init__()

        self.nseg = segments
        self.diam = diameter
        self.L = length
        self.Ra = 70

        # self.insert('hh')
        self.insert('extracellular')


class Node(SuperCompartment):

    def __init__(self, segments, length, diameter):
        super(Node, self).__init__(segments, length, diameter)

        self.insert('hh')
        self.cm = 2
        self.gnabar_hh = 3 # 1  # S/cm2
        self.gnapbar = 0.01
        self.gkbar_hh =0.08 # 0.2
        self.gl_hh =0.007 # 1e-5
        self.ena = 50  # mV
        self.ek = -90 #-77  # mV
        self.el_hh = -90 #-54.3  # mV
