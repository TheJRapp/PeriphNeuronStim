# This file contains simulation protocols for threshold search of the enumerated phrenicus experiments.
# Parameters in the function:
# - x-offset of the nerve shape
# - z-offset of the nerve shape
# - x-offset and z-offset of the nerve shape
# Possible outputs:
# - Thresholds (either in E-field amplitude or coil current)
# - AFs, E-field along axon, potential along axon
# Output format: csf (via Pandas dataframe)
#
# Other parameters, set in the GUI: E-field, Smooth field, Nerve_shape, Stimulus, Axon-diameters
# Created: 25.01.2023
# Author: J Rapp
x_search = False
z_search = False
shift = False

class ExperimentProtocol:

    def __init__(self, main_widget, interpol_rad, nerve_shape_step, shift=True, threshold=False):
        super(ExperimentProtocol, self).__init__()

        self.master_widget = main_widget


    def threshold_search(self):
        # Transfer to main file
        if not self.nerve_widget.nerve_dict:
            return
        selected_nerve = self.nerve_widget.nerve_dict[self.nerve_widget.nerve_combo_box.currentText()]
        if not selected_nerve.axon_list:
            return

        

        export_dict = {'Diameter': []}
        for axon in selected_nerve.axon_list:
            export_dict['Diameter'].append(axon.diameter)

            if x_search:
                self.run_x_search(axon,export_dict)
            elif z_search:

            elif x_search and z_search:

            elif shift:
                shift_search(x_search, z_search)

            # Set position parameter
            # z-offset only


            # z-offset and x-offset (different e-fields)
            z_offset = np.arange(-25000, 26000, 1000)
            export_dict['z-offset'] = z_offset
            for filename in sorted(field_path):
                print(str(os.path.basename(filename)))
                with open(filename, 'rb') as e:
                    self.e_field_widget.e_field_list = pickle.load(e)
                export_dict[os.path.basename(filename)] = []
                self.e_field_widget.smooth_e_field()

                self.e_field_widget.nerve_shape.z = self.e_field_widget.nerve_shape.z + z
                if self.e_field_widget.state == self.e_field_widget.E_FIELD_ONLY:
                    neuron_sim = ns.NeuronSimEField(self.e_field_widget.e_field_list, interpolation_radius_index,
                                                    axon, self.time_axis, self.stimulus, self.total_time)
                elif self.e_field_widget.state == self.e_field_widget.NERVE_SHAPE_ONLY:
                    neuron_sim = ns.NeuronSimNerveShape(self.e_field_widget.nerve_shape, nerve_shape_step_size,
                                                        axon, self.time_axis, self.stimulus, self.total_time)
                elif self.e_field_widget.state == self.e_field_widget.E_FIELD_WITH_NERVE_SHAPE:
                    neuron_sim = ns.NeuronSimEFieldWithNerveShape(self.e_field_widget.e_field_list,
                                                                  interpolation_radius_index,
                                                                  self.e_field_widget.nerve_shape, nerve_shape_step_size,
                                                                  axon, self.time_axis, self.stimulus, self.total_time)
                neuron_sim.quasipot()
                threshold = neuron_sim.threshold_simulation(self.threshold_widget)
                self.threshold_label.setText(str(threshold))
                current = 6000 * threshold
                self.e_field_widget.nerve_shape.z = self.e_field_widget.nerve_shape.z - z
                export_dict[z].append(current)
        df = pd.DataFrame(export_dict)
        today = date.today()
        df.to_csv(str(today) + 'phrenic_fo8_diam_vs_z_offset_x_8_RECT.csv', index=False, header=True)
        print('Finished!')

    def threshold_search(self):
        if not self.nerve_widget.nerve_dict:
            return
        selected_nerve = self.nerve_widget.nerve_dict[self.nerve_widget.nerve_combo_box.currentText()]
        if not selected_nerve.axon_list:
            return
        # Dict -----------------------------------------------------------------
        export_dict = {'Diameter': []}
        for axon in selected_nerve.axon_list:
            export_dict['Diameter'].append(axon.diameter)
            z_offset = np.arange(-25000, 26000, 1000)
            for z in z_offset:
                if z not in export_dict:
                    export_dict[z] = []
                self.e_field_widget.nerve_shape.z = self.e_field_widget.nerve_shape.z + z
                if self.e_field_widget.state == self.e_field_widget.E_FIELD_ONLY:
                    neuron_sim = ns.NeuronSimEField(self.e_field_widget.e_field_list, interpolation_radius_index,
                                                    axon, self.time_axis, self.stimulus, self.total_time)
                elif self.e_field_widget.state == self.e_field_widget.NERVE_SHAPE_ONLY:
                    neuron_sim = ns.NeuronSimNerveShape(self.e_field_widget.nerve_shape, nerve_shape_step_size,
                                                        axon, self.time_axis, self.stimulus, self.total_time)
                elif self.e_field_widget.state == self.e_field_widget.E_FIELD_WITH_NERVE_SHAPE:
                    neuron_sim = ns.NeuronSimEFieldWithNerveShape(self.e_field_widget.e_field_list,
                                                                  interpolation_radius_index,
                                                                  self.e_field_widget.nerve_shape, nerve_shape_step_size,
                                                                  axon, self.time_axis, self.stimulus, self.total_time)
                neuron_sim.quasipot()
                threshold = neuron_sim.threshold_simulation(self.threshold_widget)
                self.threshold_label.setText(str(threshold))
                current = 6000 * threshold
                self.e_field_widget.nerve_shape.z = self.e_field_widget.nerve_shape.z - z
                export_dict[z].append(current)
        df = pd.DataFrame(export_dict)
        today = date.today()
        df.to_csv(str(today) + 'phrenic_fo8_diam_vs_z_offset_x_8_RECT.csv', index=False, header=True)
        print('Finished!')

    def threshold_search_with_shift(self):
        if not self.nerve_widget.nerve_dict:
            return
        selected_nerve = self.nerve_widget.nerve_dict[self.nerve_widget.nerve_combo_box.currentText()]
        if not selected_nerve.axon_list:
            return
        # Dict -----------------------------------------------------------------
        offset = [0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700]
        exp_name = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r']
        for l, e in zip(offset, exp_name):
            export_dict = {'Diameter': []}
            for axon in selected_nerve.axon_list:
                export_dict['Diameter'].append(axon.diameter)
                z_offset = np.arange(-25000, 26000, 1000)
                for z in z_offset:
                    if z not in export_dict:
                        export_dict[z] = []

                    nerve_shape = deepcopy(self.e_field_widget.nerve_shape)
                    new_x, new_y, new_z = mf.generate_new_start_point(nerve_shape.x[0], nerve_shape.y[0],
                                                                      nerve_shape.z[0], nerve_shape.x[28],
                                                                      nerve_shape.y[28], nerve_shape.z[28], l)
                    nerve_shape.x[0] = new_x
                    nerve_shape.y[0] = new_y
                    nerve_shape.z[0] = new_z
                    nerve_shape.z = nerve_shape.z + z
                    if self.e_field_widget.state == self.e_field_widget.E_FIELD_ONLY:
                        neuron_sim = ns.NeuronSimEField(self.e_field_widget.e_field_list, interpolation_radius_index,
                                                        axon, self.time_axis, self.stimulus, self.total_time)
                    elif self.e_field_widget.state == self.e_field_widget.NERVE_SHAPE_ONLY:
                        neuron_sim = ns.NeuronSimNerveShape(nerve_shape, nerve_shape_step_size,
                                                            axon, self.time_axis, self.stimulus, self.total_time)
                    elif self.e_field_widget.state == self.e_field_widget.E_FIELD_WITH_NERVE_SHAPE:
                        neuron_sim = ns.NeuronSimEFieldWithNerveShape(self.e_field_widget.e_field_list,
                                                                      interpolation_radius_index, nerve_shape,
                                                                      nerve_shape_step_size,
                                                                      axon, self.time_axis, self.stimulus, self.total_time)

                    neuron_sim.quasipot()
                    threshold = neuron_sim.threshold_simulation(self.threshold_widget)
                    self.threshold_label.setText(str(threshold))
                    current = 6000 * threshold
                    nerve_shape.z = nerve_shape.z - z
                    export_dict[z].append(current)
            df = pd.DataFrame(export_dict)
            today = date.today()
            df.to_csv('020_' + e + e + '.csv', index=False, header=True)
        print('Finished!')

    def run_x_search(self, axon, exportdict):
        master = self.master_widget
        export_dict = exportdict
        x_offset = np.arange(-25000, 26000, 1000)
        for x in x_offset:
            if x not in export_dict:
                export_dict[x] = []
                master.input_data_widget.nerve_shape.z = master.input_data_widget.nerve_shape.z + z
                self.simulate(axon)

                threshold = neuron_sim.threshold_simulation(self.threshold_widget)
                self.threshold_label.setText(str(threshold))
                current = 6000 * threshold
                self.e_field_widget.nerve_shape.z = self.e_field_widget.nerve_shape.z - z
                export_dict[z].append(current)
        return # some list of offset th currents

    def run_z_search(diam):
        z_offset = np.arange(-25000, 26000, 1000)
        for z in z_offset:
            if z not in export_dict:
                export_dict[z] = []

    def simulate(self, axon, threshold=False):
        master = self.master_widget
        if master.input_data_widget.state == master.input_data_widget.NERVE_SHAPE_ONLY:
            neuron_sim = ns.NeuronSimNerveShape(master.input_data_widget.nerve_shape, nerve_shape_step_size,
                                                axon, master.time_axis, master.stimulus, master.total_time)
        elif master.input_data_widget.state == master.input_data_widget.E_FIELD_WITH_NERVE_SHAPE:
            neuron_sim = ns.NeuronSimEFieldWithNerveShape(master.input_data_widget.e_field_list,
                                                          interpolation_radius_index,
                                                          master.input_data_widget.nerve_shape, nerve_shape_step_size,
                                                          axon, master.time_axis, master.stimulus, master.total_time)
        else:
            neuron_sim = ns.NeuronSimEField(master.input_data_widget.e_field_list, interpolation_radius_index,
                                            axon, master.time_axis, master.stimulus, master.total_time)
        neuron_sim.quasipot()
        if threshold:
            threshold = neuron_sim.threshold_simulation(master.threshold_widget)
            return threshold
        else:
            return neuron_sim.mdf, neuron_sim.axon.e_field_along_axon, neuron_sim.axon.potential_along_axon

    def shift_search(xsearch,zsearch):
        return