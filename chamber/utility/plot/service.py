"""Plot utility service."""


import matplotlib
matplotlib.use('TkAgg')  # Required in order to cooporate with tkinter
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402


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

        # Examine the length of plots to determine rows and columns
        rows = len(layout.plots)
        cols = 1
        _, ax = plt.subplots(nrows=rows, ncols=cols)

        # Flatten the ax nparray if we have more than 1 plot
        if len(layout.plots) == 1:
            axes = [ax]
        else:
            axes = ax.flatten()

        # Iterate and plot
        for plot, ax in zip(layout.plots, axes):
            x = np.array(plot.abscissa.values)
            sig_x = np.array(plot.abscissa.sigma)
            for count, y_ax in enumerate(plot.axes):
                # If this is the first axis then just plot
                if count == 0:
                    this_ax = ax
                    this_ax.set(xlabel=plot.x_label)
                else:  # We need a new yaxis that shares the x-axis
                    this_ax = ax.twinx()
                for data in y_ax.data:
                    y = np.array(data.values)
                    sig_y = np.array(data.sigma)
                    label = data.label
                    # Check if the error bars are present
                    if sum(sig_x) and sum(sig_y):
                        if y_ax.error_type.lower() == 'continuous':
                            this_ax.plot(x, y)
                            this_ax.fill_between(
                                x, y-sig_y, y+sig_y, color='gray', alpha=0.2)
                            this_ax.fill_betweenx(
                                y, x-sig_x, x+sig_x, color='gray', alpha=0.2)
                        else:
                            this_ax.errorbar(x, y, xerr=sig_x, yerr=sig_y, label=label)
                    elif sum(sig_y):
                        if y_ax.error_type.lower() == 'continuous':
                            this_ax.plot(x, y)
                            this_ax.fill_between(
                                x, y-sig_y, y+sig_y, color='gray', alpha=0.2)
                        else:
                            this_ax.errorbar(x, y, yerr=sig_y, label=label)
                    elif sum(sig_x):
                        if y_ax.error_type.lower() == 'continuous':
                            this_ax.plot(x, y)
                            this_ax.fill_betweenx(
                                y, x-sig_x, x+sig_x, color='gray', alpha=0.2)
                        else:
                            this_ax.errorbar(x, y, xerr=sig_x, label=label)
                    else:
                        this_ax.plot(x, y, label=label)
                # Format the y-axis before moving on
                this_ax.set(ylabel=y_ax.y_label)
                if plot.legend:
                    this_ax.legend()
        # Show the plot
        plt.tight_layout()
        plt.show()

    # ------------------------------------------------------------------------
    # Internal methods: not included in the API

    pass
