"""Data manager service."""

import time
import tkinter as tk
from tkinter import filedialog
import os

from chamber.access.experiment.service import ExperimentAccess
from chamber.engine.analysis.service import AnalysisEngine
from chamber.utility.plot.service import PlotUtility


class DataManager(object):
    """Data manager."""

    def __init__(self):
        """Constructor."""
        self._exp_acc = ExperimentAccess()
        self._plt_util = PlotUtility()
        self._anlys_eng = AnalysisEngine(1)

    # ------------------------------------------------------------------------
    # Public methods: included in the API

    def run(self):
        """TODO: Docstring."""
        self._add_data()
        self._anlys_eng.process_fits(self._raw_data)

    # ------------------------------------------------------------------------
    # Internal methods: not included in the API

    def _add_data(self):
        path = self._get_path()
        print('Loading tdsm file...')
        self._raw_data = self._exp_acc.get_raw_data(path)
        print('Success!')
        layout = self._exp_acc.layout_raw_data(self._raw_data)
        self._plt_util.plot(layout)
        response = input(
            'Would you like to enter the experiment into the database ([y]/n)? '
            ).lower()
        if (not response) or ('y' in response):
            try:
                print('Adding data to database...')
                response = self._exp_acc.add_raw_data(self._raw_data)
            except Exception as e:
                print(e)
            else:
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
