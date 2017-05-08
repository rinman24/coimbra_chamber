"""Docstring."""

from math import pi, sqrt

from chamber.const import LAM, POW, W_0

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
        self.set_half_angle_divergence()
        self.set_peak_intensity()
        self.set_norm_coeff_profile()

    def set_rayleigh(self):
        """Use radius and wavelength to calculate Rayleigh length [m]."""
        self.rayleigh = pi * self.radius**2 / self.lam

    def set_half_angle_divergence(self):
        """Use radius and wavelength to set the half-angle divergence [radians]."""
        self.divergence_half = self.lam/(pi*self.radius)

    def set_peak_intensity(self):
        """Use radius and power to set the peak intensity; i.e., at r = 0 [W/m^2]."""
        self.peak_intensity = 2 * self.power / (pi * self.radius**2)

    def set_norm_coeff_profile(self):
        """Use radius and power to set the normalization coefficient for radial profile."""
        self.norm_coeff = 2 * sqrt(2) * self.power / (pi**1.5 * self.radius**3.)

    def get_radial_profile_grid(self):
        """Use radius to return a grid for the beam profile.
        The grid for the profile goes from -2*W to 2*W in steps of W/100 [m].
        """
        return [x*self.radius*0.01 for x in range(-200, 201)]
