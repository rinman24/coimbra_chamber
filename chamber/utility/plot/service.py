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
        x = plot.abscissae.values
        sig_x = plot.abscissae.sigma
        y = plot.ordinates.values
        sig_y = plot.ordinates.sigma
        label = plot.ordinates.label
        # Check if there are error bars present
        if sum(plot.abscissae.sigma) and sum(plot.ordinates.sigma):
            ax.errorbar(x, y, xerr=sig_x, yerr=sig_y, label=label)
        elif sum(plot.ordinates.sigma):
            ax.errorbar(x, y, yerr=sig_y, label=label)
        elif sum(plot.abscissae.sigma):
            ax.errorbar(x, y, xerr=sig_x, label=label)
        else:
            ax.plot(x, y, label=label)

        # Get fomatting information
        xlabel = plot.abscissae.axis
        ylabel = plot.ordinates.axis
        title = plot.title
        # set up the axis
        ax.set(xlabel=xlabel, ylabel=ylabel, title=title)

        # add the legend
        ax.legend()
        # Show the plot
        plt.show()

    # ------------------------------------------------------------------------
    # Internal methods: not included in the API

    pass
