"""Data manager service."""

import dacite
import time
import tkinter as tk
from tkinter import filedialog
import os

from coimbra_chamber.access.experiment.service import ExperimentAccess
from coimbra_chamber.engine.analysis.service import AnalysisEngine
from coimbra_chamber.utility.io.service import IOUtility
from coimbra_chamber.utility.io.contracts import Prompt
from coimbra_chamber.utility.plot.service import PlotUtility


class DataManager(object):
    """Data manager."""

    _confirm_acceptable_data_prompt = dacite.from_dict(
        Prompt,
        dict(messages=['Would you like to continue? [y]/n: ']))

    def __init__(self):
        """Constructor."""
        self._exp_acc = ExperimentAccess()
        self._plt_util = PlotUtility()
        self._io_util = IOUtility()

    # ------------------------------------------------------------------------
    # Public methods: included in the API

    def run(self):
        """Run an analysis for a given experiment."""
        try:
            self._add_data()
            self._anlys_eng.process_fits(self._raw_data)
        except Exception as e:
            print(f'Error: {e}')
            self._success = False
        else:
            self._success = True
            print('Successfully completed analysis and persisted data.')

    # ------------------------------------------------------------------------
    # Internal methods: not included in the API

    def _add_data(self):
        path = self._get_path()
        print('Loading tdsm file...')
        self._raw_data = self._exp_acc.get_raw_data(path)
        print('Success!')
        layout = self._exp_acc.layout_raw_data(self._raw_data)
        self._plt_util.plot(layout)
        response = self._io_util.get_input(self._confirm_acceptable_data_prompt)
        if (not response) or ('y' in response):
            try:
                print('Adding data to database...')
                response = self._exp_acc.add_raw_data(self._raw_data)
            except Exception as e:
                print(e)
            else:
                self._anlys_eng = AnalysisEngine(response['experiment_id'])
                return response

    def _get_path(self):
        """Get path as a string."""
        application_window = tk.Tk()
        application_window.withdraw()
        filename = filedialog.askopenfilename(
            parent=application_window, initialdir=os.getcwd(),
            title='Please select a file:')
        time.sleep(0.5)
        application_window.update()
        application_window.destroy()
        return filename
