"""Plot utility service."""


import matplotlib.pyplot as plt


class PlotUtility(object):
    """Plot utility."""

    # ------------------------------------------------------------------------
    # Public methods: included in the API

    def plot(self, layout):
        """Plot."""
        # Set the style if it is available
        if layout.style in plt.style.available:
            plt.style.use(layout.style)
        else:
            plt.style.use('default')
        # NOTE: We need to make this a bit more general here
        _, ax = plt.subplots(nrows=layout.rows, ncols=layout.columns)

        # Get the plot
        plot = layout.plots[0]

        # Get pointers to the values
        x = plot.abscissae[0].values
        sig_x = plot.abscissae[0].sigma
        y = plot.ordinates[0].values
        sig_y = plot.ordinates[0].sigma
        label = plot.ordinates[0].label
        # Check if there are error bars present
        if sum(sig_x) and sum(sig_y):
            ax.errorbar(x, y, xerr=sig_x, yerr=sig_y, label=label)
        elif sum(sig_y):
            ax.errorbar(x, y, yerr=sig_y, label=label)
        elif sum(sig_x):
            ax.errorbar(x, y, xerr=sig_x, label=label)
        else:
            ax.plot(x, y, label=label)

        # Format plot
        ax.set(xlabel=plot.x_label, ylabel=plot.y_label, title=plot.title)

        # Add the legend
        ax.legend()

        # Show the plot
        plt.show()

    # ------------------------------------------------------------------------
    # Internal methods: not included in the API

    pass
