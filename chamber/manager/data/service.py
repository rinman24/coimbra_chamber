"""Module encapsulates data manager."""


class DataManager(object):
    """Encapsulates all aspects "what" to do with data."""

    def add_exp(self):
        """
        Add an experiment to the database.

        NOTE: Should also plot the data and show it to the user.

        Parameters
        ----------
        io : str ir pathlib.Path

        Returns
        -------
        str
            Message detailing success or exception.

        """
        # Call the analysis engine and tell it to add some data
        # raw_data = self.anlys_eng.get_raw_data()
        # proceed = self.pres_eng.display(raw_data)
        # if proceed:
        #    try:
        #         result = self.anlys_eng.add_raw_data()
        #    except:
        #         print('Failed for some reason.')
        #         return False
        #    else:
        #         return result
        raise NotImplementedError

    def fit(self, test_id, type='chi2'):
        """
        Fit experimental data.

        NOTE: Should allow user to select a specific area to fit.
        NOTE: Should also persist the data in to the database when it is done.

        Parameters
        ----------
        test_id : int
            Primary key for the test in the sql database.
        type : {'chi2', 'exp'}
            Type of fitting to perform.
            TODO: Add more detail.

        Returns
        -------
        str
            Message detailing success or exception.      

        """
        raise NotImplementedError

    def model(self, result_id):
        """
        Model fluxes from observations.

        Parameters
        ----------
        result_id : int
            Primary key for the result in the sql database.

        Returns
        -------
        str
            Message detailing success or exception.

        """
        raise NotImplementedError

    def non_dim(self):
        """
        Nondimensionalize a result.

        Obtain Nu, Sh, Gr, Ra, etc.

        TODO: Parameters and return value.

        """
        raise NotImplementedError

    def prepare_fig(self):
        """
        Prepare a figure for publication.

        TODO: Parameters and return value.

        """
        raise NotImplementedError
