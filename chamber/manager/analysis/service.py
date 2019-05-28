"""Analysis manager service."""

import time
import tkinter as tk
from tkinter import filedialog
import os

from chamber.access.experiment.service import ExperimentAccess
from chamber.utility.plot.service import PlotUtility


class AnalysisManager(object):
    """Analysis manager."""

    def __init__(self):
        """Constructor."""
        self._exp_acc = ExperimentAccess()
        self._plt_util = PlotUtility()

    # ------------------------------------------------------------------------
    # Public methods: included in the API

    def add_data(self):
        """Add data."""
        path = self._get_path()  # None -> str
        data_spec = self._exp_acc.get_raw_data(path)  # str -> DataSpec
        # Here we actually want to call experiment access plot raw data
        layout = self._exp_acc.layout_raw_data(data_spec)
        # Plot
        self._plt_util.plot(layout)
        # NOTE: Before you go any further you need to make sure that you have
        # a test for the exp_acc.layout_raw_data(data_spec)
        # This is what is causing the failure.
        # # Then the manager needs to ask for a response
        # response = self._ask_to_proceed('Would you like to enter the experiment into the database?: ')
        # if response:
        #     try:
        #         response = self._exp_acc.persist_raw_data(raw_data)  # DTO -> DTO
        #     except:
        #         print('Something went wrong.')
        #     else:
        #         return response  # DTO

    # ------------------------------------------------------------------------
    # Internal methods: not included in the API

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
