import sys

sys.path.insert(0, "C:/nrn/lib/python")

import numpy as np
import neuron
import nrn


# Do we just need Axons or Soma, Dentrites, etc as well?
# If so: arbitrary class CellCompartment; then class Axon(CellCompartment); class Soma(CellCompartment); etc...
class Axon(object):

    def __init__(self, parameters, x=500, y=500, z=500, STIN_number=6, node_internode_pairs=10):

        self.sections = []
        self.node_length = parameters.L_node
        self.internode_length = parameters.total_internode_length
        self.name = "MRG, " + "\u2300 = " + str(parameters.D_fiber)
        self.diameter = parameters.D_fiber
        
        node = Node(parameters)
        self.sections.append(node)

        for i in range(node_internode_pairs-1):
            mysa_1 = MYSA(parameters)
            mysa_1.connect(self.sections[-1], 1)
            self.sections.append(mysa_1)

            flut_1 = FLUT(parameters)
            flut_1.connect(self.sections[-1], 1)
            self.sections.append(flut_1)

            for j in range(STIN_number):
                stin = STIN(parameters)
                stin.connect(self.sections[-1], 1)
                self.sections.append(stin)

            flut_2 = FLUT(parameters)
            flut_2.connect(self.sections[-1], 1)
            self.sections.append(flut_2)

            mysa_2 = MYSA(parameters)
            mysa_2.connect(self.sections[-1], 1)
            self.sections.append(mysa_2)

            node = Node(parameters)
            node.connect(self.sections[-1], 1)
            self.sections.append(node)

        mysa_1 = MYSA(parameters)
        mysa_1.connect(self.sections[-1], 1)
        self.sections.append(mysa_1)

        flut_1 = FLUT(parameters)
        flut_1.connect(self.sections[-1], 1)
        self.sections.append(flut_1)

        for k in range(STIN_number):
            stin = STIN(parameters)
            stin.connect(self.sections[-1], 1)
            self.sections.append(stin)

        flut_2 = FLUT(parameters)
        flut_2.connect(self.sections[-1], 1)
        self.sections.append(flut_2)

        mysa_2 = MYSA(parameters)
        mysa_2.connect(self.sections[-1], 1)
        self.sections.append(mysa_2)

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

    def __init__(self, parameters):
        super(SuperCompartment, self).__init__()

        self.nseg = parameters.nseg
        self.insert('extracellular')


class Node(SuperCompartment):

    def __init__(self, parameters):
        super(Node, self).__init__(parameters)

        self.diam = parameters.nodeD
        self.L = parameters.L_node  # length
        self.Ra = parameters.rhoa / 10000  # axial resistance, Ohm*cn

        # Hodgkin-Huxley
        self.insert('hh')
        self.gnapbar = 0.01  # persistant Na conductance
        self.gnabar_hh = 3.0  # maximum fast Na conductance
        self.gkbar_hh = 0.08  # maximum slow K conductance
        self.gl_hh = 0.007  # nodal leakage conductance
        self.ena = 50  # mV, Nernst potential Na
        self.ek = -90  # mV, Nernst potential K
        self.el_hh = -90  # mV, leakage reversal potential
        self.cm = 2

        # extracellular: for Gan and Gm, Cm
        self.xraxial[0] = parameters.Rpn0  # periaxonal resistance
        self.xg[0]= 1e10  # conductivity betw. layer
        self.xc[0]= 0

        # self.vtraub = -80
        # self.ampA = 0.01
        # self.ampB = 27
        # self.ampC = 10.2
        # self.bmpA = 0.00025
        # self.bmpB = 34
        # self.bmpC = 10
        # self.amA = 1.86
        # self.amB = 21.4
        # self.amC = 10.3
        # self.bmA = 0.086
        # self.bmB = 25.7
        # self.bmC = 9.16
        # self.ahA = 0.062
        # self.ahB = 114.0
        # self.ahC = 11.0
        # self.bhA = 2.3
        # self.bhB = 31.8
        # self.bhC = 13.4
        # self.asA = 0.3
        # self.asB = -27
        # self.asC = -5
        # self.bsA = 0.03
        # self.bsB = 10
        # self.bsC = -1

class MYSA(SuperCompartment):

    def __init__(self, parameters):
        super(MYSA, self).__init__(parameters)

        self.diam = parameters.D_fiber
        self.L = parameters.L_MYSA
        # self.Ra = parameters.rhoa * (1 / np.power((parameters.para_MYSA / parameters.D_fiber), 2)) / 10000
        self.Ra = 70
        self.cm = 2 * parameters.para_MYSA/parameters.D_fiber  # 0.69, but 0.1 in paper

        self.insert('pas')
        self.g_pas = 0.001*parameters.para_MYSA/parameters.D_fiber
        self.e_pas = -80

        self.xraxial[0]= parameters.Rpn1
        self.xg[0]= parameters.mygm/(parameters.nl*2)
        self.xc[0]= parameters.mycm/(parameters.nl*2)


class FLUT(SuperCompartment):

    def __init__(self, parameters):
        super(FLUT, self).__init__(parameters)

        self.diam = parameters.D_fiber
        self.L = parameters.L_FLUT
        # self.Ra = parameters.rhoa * np.power(1 / (parameters.para_FLUT / parameters.D_fiber), 2) / 10000
        self.Ra = 70
        self.cm = 2 * parameters.para_FLUT / parameters.D_fiber

        self.insert('pas')
        self.g_pas = 0.0001 * parameters.para_FLUT / parameters.D_fiber
        self.e_pas = -80

        self.xraxial[0]= parameters.Rpn2
        self.xg[0]= parameters.mygm / (parameters.nl * 2)
        self.xc[0]= parameters.mycm / (parameters.nl * 2)


class STIN(SuperCompartment):

    def __init__(self, parameters):
        super(STIN, self).__init__(parameters)

        self.diam = parameters.D_fiber
        self.L = parameters.L_STIN
        # self.Ra = parameters.rhoa * np.power(1 / (parameters.axonD / parameters.D_fiber), 2) / 10000
        self.Ra = 70
        self.cm = 2 * parameters.axonD / parameters.D_fiber

        self.insert('pas')
        self.g_pas = 0.0001 * parameters.axonD / parameters.D_fiber
        self.e_pas = -80

        self.xraxial[0]= parameters.Rpx
        self.xg[0]= parameters.mygm / (parameters.nl * 2)
        self.xc[0]= parameters.mycm / (parameters.nl * 2)