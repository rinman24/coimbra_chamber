"""Docstring."""

from math import pi, sqrt, exp

import matplotlib.pyplot as plt
from matplotlib import rc
FONT = {'family': 'Times New Roman', 'weight': 'normal', 'size': 15}
rc('font', **FONT)
from mpl_toolkits.mplot3d import Axes3D

from chamber.const import LAM, POW, W_0, HWHM_COEFF_W

class GaussianBeam(object):
    """GaussianBeam type contains methods related to Gaussian laser beams."""
    def __init__(self, lam=LAM, power=POW, radius=W_0):
        """Use wavelength, power, and 1/e^2 waist radius to instanciate a Gaussian laser beam.

        Keyword arguments:
        lam -- wavelength [m] of the laser (default 10.59e-6)
        power -- total power [W] transmitted by the beam (default 20)
        radius -- 1/e^2 radius [m] of the beam (default 0.9e-3)

        Returns:
        GaussianBeam object
        """
        self.lam = lam
        self.power = power
        self.radius = radius
        self.set_rayleigh()
        self.set_div_half()
        self.set_irr_max()
        self.set_r_points()
        self.set_az_points()
        self.set_profile()
        self.set_profile_3d()

    def set_rayleigh(self):
        """Use radius and wavelength to calculate Rayleigh length [m]."""
        self.rayleigh = pi * self.radius**2 / self.lam

    def set_div_half(self):
        """Use radius and wavelength to set the half-angle divergence [radians]."""
        self.div_half = self.lam/(pi*self.radius)

    def set_irr_max(self):
        """Use radius and power to set the normalization coefficient for radial profile."""
        self.irr_max = 2 * self.power / (pi * self.radius**2)

    def set_r_points(self):
        """Use radius to set the points of the radial beam profile.

        The points for the profile go from -2*W to 2*W in steps of W/100 [m].
        """
        self.r_points = [i*self.radius*0.01 for i in range(0, 201)]

    def set_az_points(self):
        """Use a list comprehension to set points in the azimuthal beam profile.

        The points for the profile go from 0 to 2*pi in steps of pi/100 [rad].
        """
        self.az_points = [i*0.01*pi for i in range(0, 201)]

    def get_irr_r(self, r_coord):
        """Use the radial coordinate to calculte the irradiance at that point.

        Positional arguments:
        r_coord -- radial distance from axis [m]

        Returns:
        irraciance [W/m^2]
        """
        return self.irr_max * exp((-2. * r_coord**2)/(self.radius**2))

    def set_profile(self):
        """Use the r_points to calculate the beam profile."""
        self.profile = [self.get_irr_r(r_coord) for r_coord in self.r_points]

    def set_profile_3d(self):
        """Use the beam profile to generate a grid for 3d plotting."""
        self.profile_3d = [[i]*201 for i in self.profile]

    def plt_pro(self):
        """Plot the beam profile."""
        # Constants used for plotting
        hwhm = HWHM_COEFF_W*self.radius
        hlf = 0.5*self.irr_max
        i_e2 = self.irr_max*exp(-2)

        # Plot the actual profile (could be rolled up into a function)
        plt.fill_between(self.r_points, self.profile, 0, color='#B6D1E6')
        plt.plot(self.r_points, self.profile, 'k', linewidth=2)
        plt.plot([0, hwhm], [hlf, hlf], 'k--', linewidth=1)
        plt.plot([hwhm, hwhm], [0, hlf], 'k--', linewidth=1)
        plt.plot([0, self.radius], [i_e2, i_e2], 'k--', linewidth=1)
        plt.plot([self.radius, self.radius], [0, i_e2], 'k--', linewidth=1)
        plt.ylim([0, 1.1*self.irr_max])
        plt.xlabel(r'radius, $r\,$ [m]')
        plt.ylabel(r"Irradiance, $I\,$ [W/m$^2$]")
        plt.show()

    #def plt_pro_3d(self):
    #   """Plot the 3D beam profile."""
    #   fig = plt.figure()
    #   ax = fig.add_subplot(111, projection='3d')


