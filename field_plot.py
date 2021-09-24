from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
import numpy as np
import misc_functions as mf
from matplotlib.figure import Figure


# - Plot E-Field in MainWindow
# - Plot E-Field with Axon
class FieldPlot():

    def __init__(self, e_field):

        self.e_x = e_field.e_x
        self.e_y = e_field.e_y
        self.e_z = e_field.e_z
        self.x = e_field.x
        self.y = e_field.y
        self.shape = e_field.shape
        # self.e_field_fig = self.plot_e_field()

    # def plot_potential_along_cable(self, stimulus_matrix, stimulus, axisname):
    #     max_value_list = self.get_single_list(stimulus, stimulus_matrix)
    #
    #     fig = plt.figure()
    #
    #     plot = plt.plot(range(len(max_value_list))[0::20], max_value_list[0::20], '-x')
    #     plt.xlabel('Axon sections')
    #     plt.ylabel(axisname)
    #     plt.grid(True)
    #
    #     return plot
    #
    # def plot_driving_function(self, mdf):
    #     fig = plt.figure()
    #     plot = plt.plot(range(len(mdf)), mdf, '-x')
    #     plt.xlabel('Axon sections')
    #     plt.ylabel('Nodes')
    #     plt.grid(True)

    def plot_e_field(self):
        fig1 = Figure()
        ax1f1 = fig1.add_subplot(111)
        ax1f1.imshow(self.e_y, extent=[min(self.y)/1e3, max(self.y)/1e3, min(self.y)/1e3, max(self.y)/1e3])
        # self.e_field_fig = fig1
        # fig1.colorbar(pos)
        return fig1

    def plot_2d_field_with_cable(self, nerve, scale):
        e_modified = self.e_y.copy()
        dim = round(self.shape/2)
        # for x, y in zip(nerve.x, nerve.y):
        #     e_modified[(int(y/scale + dim)), (int(x/scale + dim))] = 800

        e_modified[int(nerve.y/scale + dim):int(nerve.y/scale + dim + (nerve.length/scale)), int(nerve.x/scale + dim)] = 800

        fig1 = Figure()
        ax1f1 = fig1.add_subplot(111)
        ax1f1.imshow(e_modified, extent=[min(self.y)/scale, max(self.y)/scale, min(self.y)/scale, max(self.y)/scale])
        return fig1
