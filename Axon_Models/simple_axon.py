import sys

sys.path.insert(0, "C:/nrn/lib/python")

import numpy as np
import neuron
import nrn

# Do we just need Axons or Soma, Dentrites, etc as well?
# If so: arbitrary class CellCompartment; then class Axon(CellCompartment); class Soma(CellCompartment); etc...


class Axon(object):

    def __init__(self, x=500, y=500, z=500, nseg_node=1, nseg_internode=1,
                 inter_node_diameter=10, node_diameter=10,
                 node_length=1, internode_length=1e3,
                 node_internode_pairs=10):

        self.sections = []  # ObjectType: nrn.Section
        self.node_length = node_length
        self.internode_length = internode_length
        #self.name = "Simple Axon ," + "Node \u2300 = " + str(node_diameter) + ", IntNode \u2300 = " + str(inter_node_diameter)
        self.name = "Simple Axon ," + "Node \u2300 = " + "{:.2f}".format(node_diameter) + ", IntNode \u2300 = " + str(
            inter_node_diameter)

        node = Node(nseg_node, node_length, node_diameter)
        self.sections.append(node)

        for i in range(node_internode_pairs-1):
            internode = InterNode(nseg_internode, internode_length, inter_node_diameter)
            internode.connect(self.sections[-1], 1)
            self.sections.append(internode)

            node = Node(nseg_node, node_length, node_diameter)
            node.connect(self.sections[-1], 1)
            self.sections.append(node)

        internode = InterNode(nseg_internode, internode_length, inter_node_diameter)
        internode.connect(self.sections[-1], 1)
        self.sections.append(internode)

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

        self.insert('hh')
        self.insert('extracellular')


class Node(SuperCompartment):

    def __init__(self, segments, length, diameter):
        super(Node, self).__init__(segments, length, diameter)

        self.cm = 2
        self.gnabar_hh = 3 # 1  # S/cm2
        self.gnapbar = 0.01
        self.gkbar_hh =0.08 # 0.2
        self.gl_hh =0.007 # 1e-5

        self.ena = 50  # mV
        self.ek = -90 #-77  # mV
        self.el_hh = -90 #-54.3  # mV


class InterNode(SuperCompartment):

    def __init__(self, segments, length, diameter):
        super(InterNode, self).__init__(segments, length, diameter)

        self.cm = 1e-3
        self.gnabar_hh = 0
        self.gkbar_hh = 0
        self.gl_hh = 1e-5
        self.insert('pas')
        self.g_pas = 0.001*0.01
        self.e_pas = -80
