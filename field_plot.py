from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from matplotlib import cm
import numpy as np
import database
import misc_functions as mf


class FieldPlot():

    def __init__(self, storage, e_field):

        self.x_min = min(storage.get("x "))
        self.x_max = max(storage.get("x "))
        self.y_min = min(storage.get("y "))
        self.y_max = max(storage.get("y "))
        self.z_min = min(storage.get("z "))
        self.z_max = max(storage.get("z "))
        self.e_field = e_field
        # self.e_x_modified = e_field.e_x_filtered
        self.e_x = e_field.e_x
        self.e_y = e_field.e_y
        self.e_z = e_field.e_z
        self.x_Re = e_field.x_Re
        self.x_Im = e_field.x_Im
        self.y_Re = e_field.y_Re
        self.y_Im = e_field.y_Im
        self.X, self.Y = np.meshgrid(np.linspace(self.x_min, self.y_max, e_field.e_x.shape[0]), np.linspace(self.x_min, self.y_max, e_field.e_x.shape[0])) # schäbig, sollte überarbeited werden
        # X, Y = np.meshgrid(np.linspace(-80, 80, 17), np.linspace(-80, 80, 17))

    def plot_3d_field(self):

        fig = plt.figure()
        extent = [self.x_min/1000, self.x_max/1000, self.x_min/1000, self.x_max/1000]  #= np.linspace(self.x_min, self.x_max, self.field_shape)
        pos = plt.imshow(self.e_y, extent=extent)
        cbar = fig.colorbar(pos)
        cbar.set_label(r'$E_y$ in $\frac{V}{m}$')
        # plt.xticks(x_axis)
        plt.xlabel('x in mm')
        plt.ylabel('y in mm')
        # plt.title('e_x')




    def plot_stimulus_matrix(self, stimulus, title):

        fig = plt.figure()
        ax = fig.gca(projection='3d')

        stimulus = np.array(stimulus)

        X, Y = np.meshgrid(range(len(stimulus[0])), range(len(stimulus)))
        # ax.plot_surface(X, Y, stimulus, cmap=cm.coolwarm, linewidth=0, antialiased=False )

        for i in range(len(stimulus)):
            ax.plot(range(len(stimulus[0])), np.ones(len(stimulus[0])) * i, stimulus[i])
            # ax.ticklabel_format(style='sci', axis='x', scilimits=(6, 6))

        ax.set_xlabel("Time")
        ax.set_ylabel("Cable Section")
        ax.set_zlabel(title)

    def plot_potential_along_cable(self, stimulus_matrix, stimulus, axisname):
        max_value_list = self.get_single_list(stimulus, stimulus_matrix)

        fig = plt.figure()

        plot = plt.plot(range(len(max_value_list))[0::20], max_value_list[0::20], '-x')
        plt.xlabel('Axon sections')
        plt.ylabel(axisname)
        plt.grid(True)

        return plot

    def plot_driving_function(self, mdf):
        fig = plt.figure()
        plot = plt.plot(range(len(mdf)), mdf, '-x')
        plt.xlabel('Axon sections')
        plt.ylabel('Nodes')
        plt.grid(True)


def plot_2d_field_with_cable(e_field, nerve, scale, title='Nerve'):
    e_modified = e_field.e_y.copy()
    dim = round(e_field.shape/2)
    for axon in nerve.axon_list:
        for x, y in zip(axon.x, axon.y):
            e_modified[(int(y/scale) + dim), (int(x/scale) + dim)] = 1000

    fig = plt.figure()
    pos = plt.imshow(e_modified)
    plt.xlabel('x')
    plt.ylabel('y')
    fig.colorbar(pos)
    plt.title(title)


def subplot_efield_potential_driving_function(nerve, title='Nerve'):
    fig = plt.figure()
    ax1 = fig.add_subplot(3, 1, 1)
    ax2 = fig.add_subplot(3, 1, 2)
    ax3 = fig.add_subplot(3, 1, 3)

    for model in nerve.axon_list:
        quasi_pot = mf.get_nodes_only(model.sections, model.quasi_pot_list)
        e_field = mf.get_nodes_only(model.sections, model.e_field_list)
        mdf = model.mdf

        # ax1 = fig.add_subplot(3, 1, 1)
        ax1.plot(range(len(quasi_pot)), quasi_pot, '-x')
        ax1.set_ylabel('Potential (mV)')
        plt.setp(ax1.get_xticklabels(), visible=False)

        # ax2 = fig.add_subplot(3, 1, 2)
        ax2.plot(range(len(e_field)), e_field, '-x')
        ax2.set_ylabel('E_feld (V/m)')
        plt.setp(ax2.get_xticklabels(), visible=False)

        # ax3 = fig.add_subplot(3, 1, 3)
        ax3.plot(range(len(mdf)), mdf, '-x')
        ax3.set_ylabel('MDF')
        ax3.set_xlabel('Node sections')

    fig.suptitle(title)

def plot_2d_field(e_field):
    fig = plt.figure()

    pos = plt.imshow(e_field.e_y)
    fig.colorbar(pos)
    plt.title('e_y')