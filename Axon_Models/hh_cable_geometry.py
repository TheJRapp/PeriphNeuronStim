import numpy as np
from Axon_Models import hh_axon


class TiltedAxon(hh_axon.Axon):

    def __init__(self, theta, phi, x=500, y=500, z=500, nseg_node=1, node_diameter=10, node_length=1, number_of_nodes=10):
        super(TiltedAxon, self).__init__(x, y, z, nseg_node, node_diameter, node_length, number_of_nodes)

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


class BendedAxon(hh_axon.Axon):
    # create BendedAxon by combining TiltedAxons together
    def __init__(self, theta, phi, axons_number=2, x=500, y=500, z=500, nseg_node=1, node_diameter=10,
                 node_length=1, number_of_nodes=10):
        super(BendedAxon,self).__init__(x, y, z, nseg_node, node_diameter, node_length, number_of_nodes)

        self.axons_number=axons_number
        self.number_of_nodes=number_of_nodes
        self.name = "HH_d_" + str(node_diameter) + 'nnode_' + str(number_of_nodes * axons_number)

        self.axon_list = []
        axon = TiltedAxon(theta[0], phi[0], x, y, z, nseg_node, node_diameter, node_length, number_of_nodes)
        self.sections = axon.sections
        self.x=axon.x
        self.x=self.x.tolist()
        self.y=axon.y
        self.y=self.y.tolist()
        self.z=axon.z
        self.z=self.z.tolist()
        self.axon_list.append(axon)
        for i in range(axons_number-1):
            axon = TiltedAxon(theta[i+1], phi[i+1], self.axon_list[-1].x_final + node_length/2*(self.x[-1]-self.x[-2]),
                              self.axon_list[-1].y_final+ node_length/2*(self.y[-1]-self.y[-2]),
                              self.axon_list[-1].z_final + node_length/2*(self.z[-1]-self.z[-2]),
                              nseg_node, node_diameter, node_length, number_of_nodes)
            axon.sections[0].connect(self.axon_list[-1].sections[-1], 1)
            self.sections.extend(axon.sections)
            self.x.extend(axon.x.tolist())
            self.y.extend(axon.y.tolist())
            self.z.extend(axon.z.tolist())
            self.axon_list.append(axon)

        self.x = np.asarray(self.x)
        self.y = np.asarray(self.y)
        self.z = np.asarray(self.z)


    def get_unitvector(self):
        unitvector=[]
        for i in range(len(self.axon_list)):
            unitvector.append(1 / np.sqrt((self.axon_list[i].x_final - self.axon_list[i].x_initial) ** 2 + (self.axon_list[i].y_final - self.axon_list[i].y_initial) ** 2 + (self.axon_list[i].z_final - self.axon_list[i].z_initial) ** 2) * \
                              np.array([self.axon_list[i].x_final - self.axon_list[i].x_initial, self.axon_list[i].y_final - self.axon_list[i].y_initial , self.axon_list[i].z_final - self.axon_list[i].z_initial]))
        return unitvector

    def get_segment_indices(self):
        step_vector = np.zeros(len(self.get_segments()))    # to create indices/step vector for unitvector: step_vector over number of segments
        s = 1                                               # iterate so that step_vector=(0, 0, 0, ..., 1, 1, 1, ...., 2, 2, 2, ...); length of each sequence of numbers corresponds to length of axon node_internode_pairs*2
        while s < self.axons_number:                        # -> vector shows index (=corresponding axon) for every segment
            step_vector[self.number_of_nodes * s:] += 1
            s = s + 1
        return step_vector
