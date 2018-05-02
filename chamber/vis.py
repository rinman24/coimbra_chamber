import matplotlib.pyplot as plt
import pandas as pd
# First find a way to up-pickle to the df given a fp

fp = ("C:/Users/rinman/Desktop/Chamber_Results/"
      "1atm_290K_0duty_44mm_Mass_FanOff_lowRH_Data.pkl")

# Now that I have the fp, I can un-pickle the df
df = pd.read_pickle(fp)

# Now do the same with the res fp

fp = ("C:/Users/rinman/Desktop/Chamber_Results/"
      "1atm_290K_0duty_44mm_Mass_FanOff_lowRH_Res.pkl")

# Now that I have the fp, I can un-pickle res
res = pd.read_pickle(fp)

# From example @ https://matplotlib.org/examples/pylab_examples/multiple_yaxis_with_spines.html
fig, host = plt.subplots()
fig.subplots_adjust(right=0.75)

par1 = host.twinx()
par2 = host.twinx()

# Offset the right spine of par2.  The ticks and label have already been
# placed on the right by twinx above.
par2.spines["right"].set_position(("axes", 1.2))

# Having been created by twinx, par2 has its frame off, so the line of its
# detached spine is invisible.  First, activate the frame but make the patch
# and spines invisible.
make_patch_spines_invisible(par2)
# Second, show the right spine.
par2.spines["right"].set_visible(True)

p1, = host.plot([0, 1, 2], [0, 1, 2], "b-", label="Density")
p2, = par1.plot([0, 1, 2], [0, 3, 2], "r-", label="Temperature")
p3, = par2.plot([0, 1, 2], [50, 30, 15], "g-", label="Velocity")

host.set_xlim(0, 2)
host.set_ylim(0, 2)
par1.set_ylim(0, 4)
par2.set_ylim(1, 65)

host.set_xlabel("Distance")
host.set_ylabel("Density")
par1.set_ylabel("Temperature")
par2.set_ylabel("Velocity")

host.yaxis.label.set_color(p1.get_color())
par1.yaxis.label.set_color(p2.get_color())
par2.yaxis.label.set_color(p3.get_color())

tkw = dict(size=4, width=1.5)
host.tick_params(axis='y', colors=p1.get_color(), **tkw)
par1.tick_params(axis='y', colors=p2.get_color(), **tkw)
par2.tick_params(axis='y', colors=p3.get_color(), **tkw)
host.tick_params(axis='x', **tkw)

lines = [p1, p2, p3]

host.legend(lines, [l.get_label() for l in lines])

# Added
par1.spines["left"].set_position(("axes", -0.4)) # red one
par2.spines["left"].set_position(("axes", -0.2)) # green one

make_patch_spines_invisible(par1)
make_patch_spines_invisible(par2)

par1.spines["left"].set_visible(True)
par1.yaxis.set_label_position('left')
par1.yaxis.set_ticks_position('left')

par2.spines["left"].set_visible(True)
par2.yaxis.set_label_position('left')
par2.yaxis.set_ticks_position('left')

plt.tight_layout()

plt.show()

# First things first, plot Q as a function of nu


# Helper function
def make_patch_spines_invisible(ax):
    ax.set_frame_on(True)
    ax.patch.set_visible(False)
    for sp in ax.spines.values():
        sp.set_visible(False)
