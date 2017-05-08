"""Docstring."""

from math import pi

class GaussianBeam(object):
    """GaussianBeam type contains methods related to Gaussian laser beams."""
    def __init__(self, lam=10.59e-6, power=20, radius=0.9e-3):
        """Use wavelength, power, and 1/e^2 waist radius to instanciate a Gaussian laser beam.

        Keyword arguments:
        lam -- wavelength [m] of the laser (default 10.59e-6)
        radius -- 1/e^2 radius [m] of the beam (default 0.9e-3)
        power -- power [W] of the beam (default 20)

        Returns:
        GaussianBeam object
        """
        self.lam = lam
        self.power = power
        self.radius = radius
        self.set_rayleigh()

    def set_rayleigh(self):
        """Use radius and wavelength to calculate Rayleigh length."""
        self.rayleigh = pi * self.radius**2 / self.lam
