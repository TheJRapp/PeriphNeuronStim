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

        Ex_re[np.isnan(Ex_re)] = 0
        Ey_re[np.isnan(Ey_re)] = 0
        Ez_re[np.isnan(Ez_re)] = 0
        Ex_im[np.isnan(Ex_im)] = 0
        Ey_im[np.isnan(Ey_im)] = 0
        Ez_im[np.isnan(Ez_im)] = 0

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

        # This is correct reshaping:
        # the text file must have three colums, first x must vary, second y and thrid z
        # if
        e_field.e_x = np.reshape(self.e_x, (len(set(z)), len(set(y)), len(set(x))))    # (0,1,2) to make sure Efield array arranged as [z,y,x] form
        e_field.e_y = np.reshape(self.e_y, (len(set(z)), len(set(y)), len(set(x))))
        e_field.e_z = np.reshape(self.e_z, (len(set(z)), len(set(y)), len(set(x))))
        e_field.e_x = np.transpose(e_field.e_x, (1, 2, 0))
        e_field.e_y = np.transpose(e_field.e_y, (1, 2, 0))
        e_field.e_z = np.transpose(e_field.e_z, (1, 2, 0))

        e_field.e_x[np.isnan(e_field.e_x)] = 0
        e_field.e_y[np.isnan(e_field.e_y)] = 0
        e_field.e_z[np.isnan(e_field.e_z)] = 0

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


class Nerve():

    def __init__(self, x, y, z, nerv_diam, name=''):
        self.axon_list = []
        self.x = x
        self.y = y
        self.z = z
        self.name = name
        self.nerve_diameter = nerv_diam
        self.axon_distribution_number = 6  # TODO: wtf is that?


class CustomNerve(Nerve):
    def __init__(self, x, y, z, resolution, angle, length, nerv_diam, name=''):
        phi = angle / 360 * 2 * np.pi
        theta = 90 / 360 * 2 * np.pi
        x_final = length * np.sin(theta) * np.cos(phi) + x  # spherical coordinates
        y_final = length * np.sin(theta) * np.sin(phi) + y
        z_final = length * np.cos(theta) + z
        x_vec = np.linspace(x, x_final, resolution)
        y_vec = np.linspace(y, y_final, resolution)
        z_vec = np.linspace(z, z_final, resolution)
        super(CustomNerve, self).__init__(x_vec, y_vec, z_vec, nerv_diam, name=name)
        self.angle = angle
        self.length = length


class NerveShape(Nerve):
    def __init__(self, x, y, z, xRe, yRe, zRe, xIm, yIm, zIm, name=''):
        super(NerveShape, self).__init__(x, y, z, nerv_diam=0, name=name)
        phase_x = []
        phase_y = []
        phase_z = []
        if xRe.size != 0:
            print('test 1')
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
        else:
            self.e_x = []
            self.e_y = []
            self.e_z = []


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
