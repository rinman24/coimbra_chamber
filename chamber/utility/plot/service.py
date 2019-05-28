"""Plot utility service."""


import matplotlib
matplotlib.use('TkAgg')  # Required in order to cooporate with tkinter
import matplotlib.pyplot as plt  # noqa: E402


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
            for abs_, ord_ in zip(plot.abscissae, plot.ordinates):
                # Get pointers to the values
                x = abs_.values
                sig_x = abs_.sigma

                y = ord_.values
                sig_y = ord_.sigma

                label = ord_.label

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
        plt.tight_layout()
        plt.show()

    # ------------------------------------------------------------------------
    # Internal methods: not included in the API

    pass
