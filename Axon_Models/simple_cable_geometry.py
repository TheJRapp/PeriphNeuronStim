import numpy as np
from Axon_Models import simple_axon
from neuron import h

class TiltedAxon(simple_axon.Axon):

    def __init__(self, theta, phi, x=500, y=500, z=500, segments=1, inter_node_diameter=10, node_diameter=10, node_length=1, internode_length=1e3,
                 node_internode_pairs=10):
        super(TiltedAxon, self).__init__(x, y, z, segments, inter_node_diameter, node_diameter, node_length, internode_length,
                 node_internode_pairs)

        self.theta = theta
        self.phi = phi
        self.x = x
        self.x_initial = x
        self.y = y
        self.y_initial = y
        self.z = z
        self.z_initial = z
        self.x_final = self.get_node_locations()[-1]*np.sin(theta)*np.cos(phi)+x    #spherical coordinates
        self.y_final = self.get_node_locations()[-1]*np.sin(theta)*np.sin(phi)+y
        self.z_final = self.get_node_locations()[-1]*np.cos(theta)+z
        self.x = self.x_initial + 1/np.sqrt((self.x_final-x)**2+(self.y_final-y)**2+(self.z_final-z)**2)*(self.x_final-x)*self.get_node_locations()  #P_new=P_i+v*|r|
        self.y = self.y_initial + 1/np.sqrt((self.x_final-x)**2+(self.y_final-y)**2+(self.z_final-z)**2)*(self.y_final-y)*self.get_node_locations()
        self.z = self.z_initial + 1/np.sqrt((self.x_final-x)**2+(self.y_final-y)**2+(self.z_final-z)**2)*(self.z_final-z)*self.get_node_locations()

    def get_unitvector(self):

        unitvector = 1/np.sqrt((self.x_final-self.x_initial)**2+(self.y_final-self.y_initial)**2+(self.z_final-self.z_initial)**2)*np.array([self.x_final-self.x_initial, self.y_final-self.y_initial ,self.z_final-self.z_initial])
        return unitvector


class BendedAxon(simple_axon.Axon):
    # create BendedAxon by combining TiltedAxons together
    def __init__(self, theta, phi, axons_number=2, x=500, y=500, z=500, segments=1, inter_node_diameter=10, node_diameter=10, node_length=1, internode_length=1e3, node_internode_pairs=None):
        super(BendedAxon, self).__init__(x, y, z, segments, inter_node_diameter, node_diameter, node_length, internode_length, node_internode_pairs[0])

        self.axons_number=axons_number
        self.node_internode_pairs=node_internode_pairs
        self.total_length = (node_length + internode_length) * sum(node_internode_pairs) + node_length
        self.name = "Simple_Axon_noded_" + "{:.2f}".format(node_diameter) + "_intNoded_" + str(
            inter_node_diameter) + '_nnode_' + str(sum(node_internode_pairs) * axons_number)


        self.axon_list = []
        axon = TiltedAxon(theta[0], phi[0], x, y, z, segments, inter_node_diameter, node_diameter, node_length, internode_length, node_internode_pairs[0])
        self.sections = axon.sections.copy()
        self.x = axon.x.copy()
        self.x = self.x.tolist()
        self.y = axon.y.copy()
        self.y = self.y.tolist()
        self.z = axon.z.copy()
        self.z = self.z.tolist()
        self.axon_list.append(axon)
        for i in range(axons_number-1):
            axon_c = TiltedAxon(theta[i+1], phi[i+1],
                              self.axon_list[-1].x_final + internode_length/(internode_length+node_length)*(self.x[-1]-self.x[-2]),
                              self.axon_list[-1].y_final+ internode_length/(internode_length+node_length)*(self.y[-1]-self.y[-2]),
                              self.axon_list[-1].z_final + internode_length/(internode_length+node_length)*(self.z[-1]-self.z[-2]),
                              segments, inter_node_diameter, node_diameter, node_length, internode_length, node_internode_pairs[i+1])
            axon_c.sections[0].connect(self.axon_list[-1].sections[-1], 1)
            self.sections.extend(axon_c.sections)
            self.x.extend(axon_c.x.tolist())
            self.y.extend(axon_c.y.tolist())
            self.z.extend(axon_c.z.tolist())
            self.axon_list.append(axon_c)

        del self.x[-1]
        del self.y[-1]
        del self.z[-1]
        h.disconnect(self.sections[-1])
        del self.sections[-1]
        np.delete(self.axon_list[-1].x, -1)
        np.delete(self.axon_list[-1].y, -1)
        np.delete(self.axon_list[-1].z, -1)
        h.disconnect(self.axon_list[-1].sections[-1])
        del self.axon_list[-1].sections[-1]

        # TODO: just a test to avoid spike at first and last segment
        # self.sections[0].Ra = 1000000
        # self.sections[1].Ra = 1000000
        # self.sections[-2].Ra = 1000000
        # self.sections[-1].Ra = 1000000
        #
        # self.axon_list[0].sections[0].Ra = 1000000
        # self.axon_list[0].sections[1].Ra = 1000000
        # self.axon_list[-1].sections[-1].Ra = 1000000
        # self.axon_list[-1].sections[-2].Ra = 1000000

        self.x = np.asarray(self.x)
        self.y = np.asarray(self.y)
        self.z = np.asarray(self.z)

    def get_unitvector(self):
        unitvector=[]
        for i in range(len(self.axon_list)):
            vector = np.array([self.axon_list[i].x_final - self.axon_list[i].x_initial,
                                                 self.axon_list[i].y_final - self.axon_list[i].y_initial,
                                                 self.axon_list[i].z_final - self.axon_list[i].z_initial])

            absolute = np.sqrt((self.axon_list[i].x_final - self.axon_list[i].x_initial) ** 2 + (
                    self.axon_list[i].y_final - self.axon_list[i].y_initial) ** 2 + (
                    self.axon_list[i].z_final - self.axon_list[i].z_initial) ** 2)
            unitvector.append(vector / absolute)
        return unitvector

    def get_segment_indices(self):
        step_vector = np.zeros(len(self.get_segments()))    # to create indices/step vector for unitvector: step_vector over number of segments
        s = 1                                               # iterate so that step_vector=(0, 0, 0, ..., 1, 1, 1, ...., 2, 2, 2, ...); length of each sequence of numbers corresponds to length of axon node_internode_pairs*2
        while s < self.axons_number:                        # -> vector shows index (=corresponding axon) for every segment
            step_vector[self.node_internode_pairs[s-1] * 2 * s:] += 1
            s = s + 1
        return step_vector

