import numpy as np


class AxonParameter():

    def __init__(self, segments=1, diameter=16):

        self.nseg = segments  # number of segments in compartment/nrn.Section
        self.L_node = 1.0  # length of node
        self.L_MYSA = 3  # adapt
        self.D_fiber = diameter # diameter of STIN and FLUT
        par_space_mysa = 0.002 # pariaxonal space width
        par_space_flut = 0.004
        par_space_stin = 0.004
        self.rhoa = 0.7e6  # Ohm-um  = 70 Ohm cm
        self.mycm = 0.1  # uF/cm2/lamella membrane
        self.mygm = 0.001  # S / cm2 / lamella membrane
        self.STIN_number = 6

        # adapt MYSA diameter
        if diameter == 5.7:
            self.g = 0.605
            self.axonD = 3.4  # FLUT diameter (according to paper)
            self.nodeD = 1.9  # node diameter
            self.para_MYSA = 1.9  # MYSA diameter (according to paper)
            self.para_FLUT = 3.4
            self.deltax = 500  # node-node separation
            self.L_FLUT = 35  # length of FLUT
            self.nl = 80

        elif diameter == 7.3:
            self.g = 0.630
            self.axonD = 4.6
            self.nodeD = 2.4
            self.para_MYSA = 2.4
            self.para_FLUT = 4.6
            self.deltax = 750
            self.L_FLUT = 38
            self.nl = 100

        elif diameter == 8.7:
            self.g = 0.661
            self.axonD = 5.8
            self.nodeD = 2.8
            self.para_MYSA = 2.8
            self.para_FLUT = 5.8
            self.deltax = 1000
            self.L_FLUT = 40
            self.nl = 110

        elif diameter == 10.0:
            self.g = 0.690
            self.axonD = 6.9
            self.nodeD = 3.3
            self.para_MYSA = 3.3
            self.para_FLUT = 6.9
            self.deltax = 1150
            self.L_FLUT = 46
            self.nl = 120

        elif diameter == 11.5:
            self.g = 0.700
            self.axonD = 8.1
            self.nodeD = 3.7
            self.para_MYSA = 3.7
            self.para_FLUT = 8.1
            self.deltax = 1250
            self.L_FLUT = 50
            self.nl = 130

        elif diameter == 12.8:
            self.g = 0.719
            self.axonD = 9.2
            self.nodeD = 4.2
            self.para_MYSA = 4.2
            self.para_FLUT = 9.2
            self.deltax = 1350
            self.L_FLUT = 54
            self.nl = 135

        elif diameter == 14.0:
            self.g = 0.739
            self.axonD = 10.4
            self.nodeD = 4.7
            self.para_MYSA = 4.7
            self.para_FLUT = 10.4
            self.deltax = 1400
            self.L_FLUT = 56
            self.nl = 140

        elif diameter == 15.0:
            self.g = 0.767
            self.axonD = 11.5
            self.nodeD = 5.0
            self.para_MYSA = 5.0
            self.para_FLUT = 11.5
            self.deltax = 1450
            self.L_FLUT = 58
            self.nl = 145

        else:   # default: if none of the specified diameters is given, it is set to 16 microns
            self.D_fiber = 16.0
            self.g = 0.791
            self.axonD = 12.7
            self.nodeD = 5.5
            self.para_MYSA = 5.5
            self.para_FLUT = 12.7
            self.deltax = 1500
            self.L_FLUT = 60
            self.nl = 150

        # Rpn0 comes as Ohm/um which is MOhm/m; 0.01 converts to MOhm/cm which is unit of xraxial
        self.Rpn0 = (self.rhoa * 0.01) / (np.pi * (((diameter / 2) + par_space_mysa)**2 - (diameter / 2)**2))
        self.Rpn1 = (self.rhoa * 0.01) / (np.pi * (((self.para_MYSA / 2) + par_space_mysa)**2 - (self.para_MYSA / 2)**2))
        self.Rpn2 = (self.rhoa * 0.01) / (np.pi * (((self.para_FLUT / 2) + par_space_flut)**2 - (self.para_FLUT / 2)**2))
        self.Rpx = (self.rhoa * 0.01) / (np.pi * (((self.axonD / 2) + par_space_stin)**2 - (self.axonD / 2)**2))
        self.L_STIN = (self.deltax - self.L_node - (2 * self.L_MYSA) - (2 * self.L_FLUT)) / self.STIN_number
        self.total_internode_length = self.L_FLUT*2 + self.L_MYSA*2 + self.L_STIN * self.STIN_number