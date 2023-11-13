import numpy as np
import neuron_sim as ns

# ToDo: Insert distribution of (a) axon diameters, (b) axon starting points within radius around centre point
class Nerve():

    def __init__(self, x, y, z, length, angle, nerv_diam, name):

        self.axon_infos_list = []
        self.x = x
        self.y = y
        self.z = z
        self.angle = angle

        self.length = length
        self.name = name
        self.nerve_diameter = nerv_diam
        self.axon_distribution_number = 6
        # self.add_models()
