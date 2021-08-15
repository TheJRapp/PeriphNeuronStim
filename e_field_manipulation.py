import pickle
import database
import file_parser
import numpy as np
from matplotlib.figure import Figure


def get_e_field(model_name):
    # storage = database.DataBase()
    # parser = file_parser.NewCSTFileParser("D:/Files/Doktorarbeit/NEURON_Phrenicus/CST_files/", "Halsmodell_E_field_Phrenic.txt")
    # parser.parse_file(storage)
    # storage.convert_units(1e3)  # convert mm from CST to um used for cable

    # Save:
    # with open("halsmodell_phrenic", 'wb') as f:
    #     pickle.dump(storage, f)

    # Load:
    # with open("20210325_halsmodell", 'rb') as f:
    #     halsmodell_storage = pickle.load(f)
    # with open("20210325_biovoxel", 'rb') as f:
    #     biovoxel_storage = pickle.load(f)

    # # Save matrix list:
    # e_field_matrix_list = storage.generate_e_field_matrix()
    # with open("Halsmodell_phrenic_e_field_matrix_list", 'wb') as f:
    #     pickle.dump(e_field_matrix_list, f)

    # Open matrix list:
    path = 'D:/Files/Doktorarbeit/NEURON_Phrenicus/CST_files/'
    with open(path + "20210325_biovoxel_e_field_matrix_list", 'rb') as e:
        biovoxel_e_field_matrix_list = pickle.load(e)
    with open(path + "20210325_halsmodell_e_field_matrix_list", 'rb') as e:
        halsmodell_e_field_matrix_list = pickle.load(e)

    if model_name == 'biovoxel':
        e_field_list = biovoxel_e_field_matrix_list

    else:
        e_field_list = halsmodell_e_field_matrix_list

        for e_field in e_field_list:
            
            # no = neck only
            e_x_no = e_field.e_x[182:228, 168:234]
            e_y_no = e_field.e_y[182:228, 168:234]
            e_z_no = e_field.e_z[182:228, 168:234]

            e_field.e_x = np.zeros((101, 101))
            y_offset = 32
            x_offset = 17
            e_field.e_x[y_offset:(y_offset + e_x_no.shape[0]), x_offset:(x_offset + e_x_no.shape[1])] = e_x_no
            e_field.e_y = np.zeros((101, 101))
            e_field.e_y[y_offset:(y_offset + e_y_no.shape[0]), x_offset:(x_offset + e_y_no.shape[1])] = e_y_no
            e_field.e_z = np.zeros((101, 101))
            e_field.e_z[y_offset:(y_offset + e_z_no.shape[0]), x_offset:(x_offset + e_z_no.shape[1])] = e_z_no

            e_field.x = e_field.x[168 - x_offset:234 + 1 + x_offset]
            e_field.y = e_field.y[182 - y_offset:228 + 1 + y_offset]
            e_field.shape = len(e_field.x[e_field.x_min:e_field.x_max+1])

    #plt.imshow(e_y)
    # plt.imshow(e_y_no)
    # plt.colorbar()
    # plt.imshow(zeros)
    # plt.show()

    return e_field_list


