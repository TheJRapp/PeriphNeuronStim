# store electric field / potential field
import numpy as np
from PIL import Image
from matplotlib import cm
import timeit


class DataBase(dict):

    def __init__(self):
        super(DataBase, self).__init__()

        self.captions = []

    def convert_units(self, factor=1):
        for i in range(len(self.get("x "))):
            self.get("x ")[i] = factor * self.get("x ")[i]
            self.get("y ")[i] = factor * self.get("y ")[i]
            self.get("z ")[i] = factor * self.get("z ")[i]

    def generate_e_field_matrix(self):
        # x_dimensions and y_dimensions of e_field must be the same
        z_control = self.get("z ")
        layers = set(z_control)
        e_field_list = []
        for layer in layers:
            layer_index = [i for i, z_control in enumerate(z_control) if z_control == layer]
            print('Layer: ', layer)
            x = np.asarray([self.get("x ")[i] for i in layer_index])
            y = np.asarray([self.get("y ")[i] for i in layer_index])
            z = np.asarray([self.get("z ")[i] for i in layer_index])
            xRe = np.asarray([self.get("xRe ")[i] for i in layer_index])
            yRe = np.asarray([self.get("yRe ")[i] for i in layer_index])
            zRe = np.asarray([self.get("zRe ")[i] for i in layer_index])
            xIm = np.asarray([self.get("xIm ")[i] for i in layer_index])
            yIm = np.asarray([self.get("yIm ")[i] for i in layer_index])
            zIm = np.asarray([self.get("zIm ")[i] for i in layer_index])

            e_field = EField(x, y, z, xRe, yRe, zRe, xIm, yIm, zIm, layer)
            e_field_list.append(e_field)
            print('...')
        return e_field_list

    def rotate_e_field(self, e_field, angle):

        e_modified = e_field.copy()
        # TODO: Ist das die Rotation in die richtige Richtung???
        e_x_rot = np.cos(np.deg2rad(angle)) * e_modified.e_x + np.sin(np.deg2rad(angle)) * e_modified.e_y
        e_y_rot = np.cos(np.deg2rad(angle)) * e_modified.e_y + np.sin(np.deg2rad(angle)) * e_modified.e_x

        e_x_image = Image.fromarray(e_x_rot)
        rotated_e_x = np.asarray(e_x_image.rotate(angle))
        e_modified.e_x = rotated_e_x

        e_y_image = Image.fromarray(e_y_rot)
        rotated_e_y = np.asarray(e_y_image.rotate(angle))
        e_modified.e_y = rotated_e_y

        return e_modified


class EField():

    def __init__(self, x, y, z, xRe, yRe, zRe, xIm, yIm, zIm, layer_selection):
        self.x = x
        self.y = y
        self.z = z
        self.layer = layer_selection
        # TODO: Braucht man nicht mehr oder?
        # self.xRe = xRe
        # self.yRe = yRe
        # self.xIm = xIm
        # self.yIm = yIm
        self.x_min = np.argmin(x)
        self.x_max = np.argmax(x)
        self.y_min = np.argmin(y)
        self.y_max = np.argmax(y)
        shape = len(x[self.x_min:self.x_max+1])
        self.shape = shape
        self.resolution = abs(x[1] - x[0])

        phase_x = []
        phase_y = []
        phase_z = []

        debugA = max(xRe)
        debugB = max(xIm)
        for i in range(x.shape[0]):
            phase_x.append(np.arccos(xRe[i] / np.sqrt(xRe[i] ** 2 + xIm[i] ** 2)) if xIm[i] >= 0 else - np.arccos(
                xRe[i] / np.sqrt(xRe[i] ** 2 + xIm[i] ** 2)))
            phase_y.append(np.arccos(yRe[i] / np.sqrt(yRe[i] ** 2 + yIm[i] ** 2)) if yIm[i] >= 0 else - np.arccos(
                yRe[i] / np.sqrt(yRe[i] ** 2 + yIm[i] ** 2)))
            phase_z.append(np.arccos(zRe[i] / np.sqrt(zRe[i] ** 2 + zIm[i] ** 2)) if zIm[i] >= 0 else - np.arccos(
                zRe[i] / np.sqrt(zRe[i] ** 2 + zIm[i] ** 2)))

        self.e_x = np.true_divide(phase_x, np.absolute(phase_x)) * np.sqrt(xRe ** 2 + xIm ** 2)
        self.e_y = np.true_divide(phase_y, np.absolute(phase_y)) * np.sqrt(yRe ** 2 + yIm ** 2)
        self.e_z = np.true_divide(phase_z, np.absolute(phase_z)) * np.sqrt(zRe ** 2 + zIm ** 2)

        if shape:
            self.e_x = np.reshape(self.e_x, (shape, shape))
            self.e_y = np.reshape(self.e_y, (shape, shape))
            self.e_z = np.reshape(self.e_z, (shape, shape))
            # TODO: Braucht man nicht mehr oder?
            # self.x_Re = np.reshape(self.xRe, (shape, shape))
            # self.x_Im = np.reshape(self.xIm, (shape, shape))
            # self.y_Re = np.reshape(self.yRe, (shape, shape))
            # self.y_Im = np.reshape(self.yIm, (shape, shape))
