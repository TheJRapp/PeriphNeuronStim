from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
import numpy as np
import misc_functions as mf
from matplotlib.figure import Figure

class FieldPlot():

    def __init__(self, e_field):

        self.e_x = e_field.e_x
        self.e_y = e_field.e_y
        self.e_z = e_field.e_z
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
        ax1f1.imshow(self.e_y)
        # self.e_field_fig = fig1
        # fig1.colorbar(pos)
        return fig1

    def plot_2d_field_with_cable(self, nerve, scale):
        e_modified = self.e_y.copy()

        e_modified[int(nerve.y):int(nerve.y+nerve.length), int(nerve.x)] = 800

        # dim = round(e_modified.shape/2)
        # for axon in nerve.axon_list:
        #     for x, y in zip(axon.x, axon.y):
        #         e_modified[(int(y/scale) + dim), (int(x/scale) + dim)] = 1000

        fig1 = Figure()
        ax1f1 = fig1.add_subplot(111)
        ax1f1.imshow(e_modified)
        # self.e_field_fig = fig1
        # fig1.colorbar(pos)
        return fig1
#
#
# def subplot_efield_potential_driving_function(nerve, title='Nerve'):
#     fig = plt.figure()
#     ax1 = fig.add_subplot(3, 1, 1)
#     ax2 = fig.add_subplot(3, 1, 2)
#     ax3 = fig.add_subplot(3, 1, 3)
#
#     for model in nerve.axon_list:
#         quasi_pot = mf.get_nodes_only(model.sections, model.quasi_pot_list)
#         e_field = mf.get_nodes_only(model.sections, model.e_field_list)
#         mdf = model.mdf
#
#         # ax1 = fig.add_subplot(3, 1, 1)
#         ax1.plot(range(len(quasi_pot)), quasi_pot, '-x')
#         ax1.set_ylabel('Potential (mV)')
#         plt.setp(ax1.get_xticklabels(), visible=False)
#
#         # ax2 = fig.add_subplot(3, 1, 2)
#         ax2.plot(range(len(e_field)), e_field, '-x')
#         ax2.set_ylabel('E_feld (V/m)')
#         plt.setp(ax2.get_xticklabels(), visible=False)
#
#         # ax3 = fig.add_subplot(3, 1, 3)
#         ax3.plot(range(len(mdf)), mdf, '-x')
#         ax3.set_ylabel('MDF')
#         ax3.set_xlabel('Node sections')
#
#     fig.suptitle(title)
#
# def plot_2d_field(e_field):
#     fig = plt.figure()
#
#     pos = plt.imshow(e_field.e_y)
#     fig.colorbar(pos)
#     plt.title('e_y')