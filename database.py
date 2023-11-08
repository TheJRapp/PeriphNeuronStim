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

    def generate_nerve_shape(self):
        x = np.asarray(self.get("x "))
        y = np.asarray(self.get("y "))
        z = np.asarray(self.get("z "))
        xRe = np.asarray(self.get("ExRe "))
        yRe = np.asarray(self.get("EyRe "))
        zRe = np.asarray(self.get("EzRe "))
        xIm = np.asarray(self.get("ExIm "))
        yIm = np.asarray(self.get("EyIm "))
        zIm = np.asarray(self.get("EzIm "))
        nerve_shape = NerveShape(x, y, z, xRe, yRe, zRe, xIm, yIm, zIm)
        return nerve_shape

    def generate_e_field_matrix(self):
        e_field = self.generate_3d_field()
        print('E-field done')
        return e_field

    def generate_3d_field(self):
        x = np.array(self.get("x "))
        y = np.array(self.get("y "))
        z = np.array(self.get("z "))
        Ex_re = np.array(self.get("ExRe "))
        Ex_im = np.array(self.get("ExIm "))
        Ey_re = np.array(self.get("EyRe "))
        Ey_im = np.array(self.get("EyIm "))
        Ez_re = np.array(self.get("EzRe "))
        Ez_im = np.array(self.get("EzIm "))

        phase_x = []
        phase_y = []
        phase_z = []

        for i in range(Ex_re.shape[0]):
            phase_x.append(np.arccos(Ex_re[i] / np.sqrt(Ex_re[i] ** 2 + Ex_im[i] ** 2)) if Ex_im[i] >= 0 else - np.arccos(
                Ex_re[i] / np.sqrt(Ex_re[i] ** 2 + Ex_im[i] ** 2)))
        # for i in range(y.shape[0]):
            phase_y.append(np.arccos(Ey_re[i] / np.sqrt(Ey_re[i] ** 2 + Ey_im[i] ** 2)) if Ey_im[i] >= 0 else - np.arccos(
                Ey_re[i] / np.sqrt(Ey_re[i] ** 2 + Ey_im[i] ** 2)))
            phase_z.append(np.arccos(Ez_re[i] / np.sqrt(Ez_re[i] ** 2 + Ez_im[i] ** 2)) if Ez_im[i] >= 0 else - np.arccos(
                Ez_re[i] / np.sqrt(Ez_re[i] ** 2 + Ez_im[i] ** 2)))

        self.e_x = np.true_divide(phase_x, np.absolute(phase_x)) * np.sqrt(Ex_re ** 2 + Ex_im ** 2)
        self.e_y = np.true_divide(phase_y, np.absolute(phase_y)) * np.sqrt(Ey_re ** 2 + Ey_im ** 2)
        self.e_z = np.true_divide(phase_z, np.absolute(phase_z)) * np.sqrt(Ez_re ** 2 + Ez_im ** 2)

        e_field = EField()
        e_field.x = np.sort(np.asarray(list(set(x))))
        e_field.y = np.sort(np.asarray(list(set(y))))
        e_field.z = np.sort(np.asarray(list(set(z))))
        e_field.e_x = np.transpose(np.reshape(self.e_x, (len(set(x)), len(set(y)), len(set(z)))), (1,2,0))
        e_field.e_y = np.transpose(np.reshape(self.e_y, (len(set(x)), len(set(y)), len(set(z)))), (1,2,0))
        e_field.e_z = np.transpose(np.reshape(self.e_z, (len(set(x)), len(set(y)), len(set(z)))), (1,2,0))

        # e_field.e_x = np.reshape(self.e_x, (len(set(x)), -1, len(set(z))))
        # e_field.e_y = np.reshape(self.e_y, (len(set(x)), -1, len(set(z))))
        # e_field.e_z = np.reshape(self.e_z, (len(set(x)), -1, len(set(z))))
        return e_field


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


class NerveShape():

    def __init__(self, x, y, z, xRe, yRe, zRe, xIm, yIm, zIm):
        self.x = x
        self.y = y
        self.z = z

        phase_x = []
        phase_y = []
        phase_z = []

        for i in range(len(x)):
            phase_x.append(np.arccos(xRe[i] / np.sqrt(xRe[i] ** 2 + xIm[i] ** 2)) if xIm[i] >= 0 else - np.arccos(
                xRe[i] / np.sqrt(xRe[i] ** 2 + xIm[i] ** 2)))
            phase_y.append(np.arccos(yRe[i] / np.sqrt(yRe[i] ** 2 + yIm[i] ** 2)) if yIm[i] >= 0 else - np.arccos(
                yRe[i] / np.sqrt(yRe[i] ** 2 + yIm[i] ** 2)))
            phase_z.append(np.arccos(zRe[i] / np.sqrt(zRe[i] ** 2 + zIm[i] ** 2)) if zIm[i] >= 0 else - np.arccos(
                zRe[i] / np.sqrt(zRe[i] ** 2 + zIm[i] ** 2)))

        self.e_x = np.true_divide(phase_x, np.absolute(phase_x)) * np.sqrt(xRe ** 2 + xIm ** 2)
        self.e_y = np.true_divide(phase_y, np.absolute(phase_y)) * np.sqrt(yRe ** 2 + yIm ** 2)
        self.e_z = np.true_divide(phase_z, np.absolute(phase_z)) * np.sqrt(zRe ** 2 + zIm ** 2)

class EFieldLayer(): # TODO: Braucht man nicht mehr oder?

    def __init__(self, x, y, z, xRe, yRe, zRe, xIm, yIm, zIm, layer_selection):
        self.x = x
        self.y = y
        self.z = z
        self.layer = layer_selection

        # self.xRe = xRe
        # self.yRe = yRe
        # self.xIm = xIm
        # self.yIm = yIm
        self.x_min = np.argmin(x)
        self.x_max = np.argmax(x)
        self.y_min = np.argmin(y)
        self.y_max = np.argmax(y)
        x_values = set(x)
        y_values = set(y)
        self.xshape = len(x_values)
        self.yshape = len(y_values)
        self.resolution = abs(x[1] - x[0])

        phase_x = []
        phase_y = []
        phase_z = []

        for i in range(x.shape[0]):
            phase_x.append(np.arccos(xRe[i] / np.sqrt(xRe[i] ** 2 + xIm[i] ** 2)) if xIm[i] >= 0 else - np.arccos(
                xRe[i] / np.sqrt(xRe[i] ** 2 + xIm[i] ** 2)))
        # for i in range(y.shape[0]):
            phase_y.append(np.arccos(yRe[i] / np.sqrt(yRe[i] ** 2 + yIm[i] ** 2)) if yIm[i] >= 0 else - np.arccos(
                yRe[i] / np.sqrt(yRe[i] ** 2 + yIm[i] ** 2)))
            phase_z.append(np.arccos(zRe[i] / np.sqrt(zRe[i] ** 2 + zIm[i] ** 2)) if zIm[i] >= 0 else - np.arccos(
                zRe[i] / np.sqrt(zRe[i] ** 2 + zIm[i] ** 2)))

        self.e_x = np.true_divide(phase_x, np.absolute(phase_x)) * np.sqrt(xRe ** 2 + xIm ** 2)
        self.e_y = np.true_divide(phase_y, np.absolute(phase_y)) * np.sqrt(yRe ** 2 + yIm ** 2)
        self.e_z = np.true_divide(phase_z, np.absolute(phase_z)) * np.sqrt(zRe ** 2 + zIm ** 2)

        if self.xshape:
            self.e_x = np.reshape(self.e_x, (self.yshape, self.xshape))
            self.e_y = np.reshape(self.e_y, (self.yshape, self.xshape))
            self.e_z = np.reshape(self.e_z, (self.yshape, self.xshape))
            # self.e_x = np.reshape(self.e_x, (self.xshape, self.yshape))
            # self.e_y = np.reshape(self.e_y, (self.xshape, self.yshape))
            # self.e_z = np.reshape(self.e_z, (self.xshape, self.yshape))
            # TODO: Braucht man nicht mehr oder?
            # self.x_Re = np.reshape(self.xRe, (shape, shape))
            # self.x_Im = np.reshape(xIm, (self.yshape, self.xshape))
            # self.y_Re = np.reshape(self.yRe, (shape, shape))
            # self.y_Im = np.reshape(self.yIm, (shape, shape))


class EField():

    def __init__(self):
        self.x = []
        self.y = []
        self.z = []
        self.e_x = []
        self.e_y = []
        self.e_z = []

    def finalize(self,):
        self.x_min = np.argmin(self.x)
        self.x_max = np.argmax(self.x)
        self.y_min = np.argmin(self.y)
        self.y_max = np.argmax(self.y)
        self.resolution = abs(self.x[1] - self.x[0])