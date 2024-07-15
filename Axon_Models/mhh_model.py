import sys

sys.path.insert(0, "C:/nrn/lib/python")

import numpy as np
import neuron
import nrn
from matplotlib import pyplot as plt

class Axon(object):

    def __init__(self, nerve_shape, nseg_node=1, nseg_internode=1, diameter=10):

        self.type = 'MHH'
        self.diameter = diameter
        node_diameter = 0.3449 * diameter - 0.1484  # um; the formula is from Olivar Izard Master's thesis
        node_length = 1
        if diameter > 4:
            internode_length = 969.3 * np.log(diameter) - 1144.6
        else:
            internode_length = 100 * diameter

        self.sections = []  # ObjectType: nrn.Section
        self.node_length = node_length
        self.internode_length = internode_length
        self.node_diameter = node_diameter
        self.nseg_node = nseg_node
        self.nseg_internode = nseg_internode

        # spacing = smallest segment length
        if self.node_length/self.nseg_node < self.internode_length / self.nseg_internode:
            self.spacing = self.node_length / (self.nseg_node)
        else:
            self.spacing = self.internode_length / (self.nseg_internode)
        self.x_coordinates, self.y_coordinates, self.z_coordinates, self.total_length = self.adapt_nerve_shape_to_axon(nerve_shape)
        self.number_node_internode_pairs = int(self.total_length / (self.internode_length + self.node_length))-1
        self.internode_start_points, self.node_start_points, self.segment_start_points = self.determine_coordinates()

        self.x = self.x_coordinates[self.segment_start_points]
        self.y = self.y_coordinates[self.segment_start_points]
        self.z = self.z_coordinates[self.segment_start_points]

        node = Node(nseg_node, node_length, node_diameter)
        self.sections.append(node)
        for i in range(self.number_node_internode_pairs):
            internode = InterNode(self.nseg_internode, self.internode_length, self.diameter)
            internode.connect(self.sections[-1], 1)
            self.sections.append(internode)
            node = Node(self.nseg_node, self.node_length, self.node_diameter)
            node.connect(self.sections[-1], 1)
            self.sections.append(node)

        self.seg_unit_vectors = self.calculate_unit_vectors()
        self.e_field_along_axon = None
        self.potential_along_axon = None
        # TODO: Implement unit vector
        print('Creating axon done')

    def adapt_nerve_shape_to_axon(self, nerve_shape):
        total_length = 0
        first = True
        for i in range(len(nerve_shape.x) - 1):
            delta = np.sqrt((nerve_shape.x[i + 1] - nerve_shape.x[i]) ** 2 + (
                    nerve_shape.y[i + 1] - nerve_shape.y[i]) ** 2
                            + (nerve_shape.z[i + 1] - nerve_shape.z[i]) ** 2)
            total_length = total_length + delta
            num_of_points = round(delta / self.spacing)
            delta_x = nerve_shape.x[i + 1] - nerve_shape.x[i]
            delta_y = nerve_shape.y[i + 1] - nerve_shape.y[i]
            delta_z = nerve_shape.z[i + 1] - nerve_shape.z[i]
            if num_of_points > 5:
                if first:
                    x_coordinates = list(np.linspace(nerve_shape.x[0], nerve_shape.x[0] + delta_x, num_of_points))
                    y_coordinates = list(np.linspace(nerve_shape.y[0], nerve_shape.y[0] + delta_y, num_of_points))
                    z_coordinates = list(np.linspace(nerve_shape.z[0], nerve_shape.z[0] + delta_z, num_of_points))
                    first = False
                else:
                    x_coordinates.extend(
                        list(np.linspace(x_coordinates[-1], x_coordinates[-1] + delta_x, num_of_points)))
                    y_coordinates.extend(
                        list(np.linspace(y_coordinates[-1], y_coordinates[-1] + delta_y, num_of_points)))
                    z_coordinates.extend(
                        list(np.linspace(z_coordinates[-1], z_coordinates[-1] + delta_z, num_of_points)))

        x_coordinates = np.asarray(x_coordinates)
        y_coordinates = np.asarray(y_coordinates)
        z_coordinates = np.asarray(z_coordinates)
        return x_coordinates, y_coordinates, z_coordinates, total_length

    def determine_coordinates(self):
        spacings_per_internode = int(self.internode_length / self.spacing)
        spacings_per_node = int(self.node_length / self.spacing)
        if spacings_per_internode == 0:
            spacings_per_internode = 1
        if spacings_per_node == 0:
            spacings_per_node = 1
        # Assigning the start points instead of the middle points --> cable is shifted for half internode length
        node_start_points = [i * (spacings_per_internode + spacings_per_node + 1) for i in
                             range(self.number_node_internode_pairs+1)]
        internode_start_points = [i + spacings_per_node for i in node_start_points]
        spacings_per_in_seg = int((self.internode_length/self.nseg_internode) / self.spacing)
        spacings_per_n_seg = int((self.node_length / self.nseg_node) / self.spacing)
        if spacings_per_in_seg == 0:
            spacings_per_in_seg = 1
        if spacings_per_n_seg == 0:
            spacings_per_n_seg = 1
        segment_start_points = []
        for j in range(self.nseg_node):
            node_seg_start_point = node_start_points
            node_seg_start_point = [i + j*spacings_per_n_seg for i in node_seg_start_point]
            segment_start_points.extend(node_seg_start_point)
        for j in range(self.nseg_internode):
            internode_seg_start_point = internode_start_points
            internode_seg_start_point = [i + spacings_per_in_seg + j*spacings_per_in_seg for i
                                         in internode_seg_start_point]
            segment_start_points.extend(internode_seg_start_point)
        segment_start_points.sort()
        return internode_start_points, node_start_points, segment_start_points

    def return_node_coordinates(self):
        return self.x_coordinates[self.node_start_points], self.y_coordinates[self.node_start_points], \
               self.z_coordinates[self.node_start_points]

    def return_internode_coordinates(self):
        return self.x_coordinates[self.internode_start_points], self.y_coordinates[self.internode_start_points], \
               self.z_coordinates[self.internode_start_points]

    def calculate_unit_vectors(self):
        seg_unit_vectors = []
        for i in range(len(self.x)-1):
            delta_x = (self.x[i + 1] - self.x[i])
            delta_y = (self.y[i + 1] - self.y[i])
            delta_z = (self.z[i + 1] - self.z[i])
            length = np.sqrt(delta_x ** 2 + delta_y ** 2 + delta_z ** 2)
            seg_unit_vectors.append([delta_x/length, delta_y/length, delta_z/length])
        seg_unit_vectors.append(seg_unit_vectors[-1])
        return seg_unit_vectors

    def get_segments(self):
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
