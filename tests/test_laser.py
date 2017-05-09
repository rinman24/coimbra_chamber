from math import exp, isclose, log, pi, sqrt

import chamber.laser as laser

class TestLaser(object):
    """Unit testing of laser.py."""

    def test_laser_constructor(self):
        """Check that a laser can be instanciated properly."""
        co2_laser = laser.GaussianBeam()
        assert co2_laser.lam == 10.59e-6
        assert co2_laser.power == 20
        assert co2_laser.radius == 0.9e-3

    def test_laser_constructor_custom(self):
        """Check that a laser can be instanciated with a custom parameters."""
        co2_laser = laser.GaussianBeam(lam=635e-9, power=5e-3, radius=4e-3)
        assert co2_laser.lam == 635e-9
        assert co2_laser.power == 5e-3
        assert co2_laser.radius == 4e-3

    def test_laser_constructor_rayleigh(self):
        """Check that rayleigh length is calculated correctly."""
        co2_laser = laser.GaussianBeam()
        assert co2_laser.rayleigh == pi * 0.9e-3**2 / 10.59e-6

    def test_laser_constructor_half_angle(self):
        """Check that half-angle divergence is calculated correctly."""
        co2_laser = laser.GaussianBeam()
        assert co2_laser.divergence_half == 10.59e-6/(pi*0.9e-3)

    def test_laser_constructor_peak_intensity(self):
        """Check that peak intensity is calculated correctly."""
        co2_laser = laser.GaussianBeam()
        assert co2_laser.peak_intensity == 2 * 20 / (pi * 0.9e-3**2)

    def test_laser_constructor_norm_coeff(self):
        """Check that normalization coefficient is calculated correctly."""
        co2_laser = laser.GaussianBeam()
        assert co2_laser.norm_coeff == 2 * sqrt(2.) * 20 / (pi**1.5 * 0.9e-3**3.)

    def test_get_irradiance_at_r(self):
        """Check that irradiance at a point is calculated correctly."""
        co2_laser = laser.GaussianBeam()
        assert co2_laser.get_irr_r(0) == co2_laser.norm_coeff
        hwhm = sqrt(2*log(2)) * (co2_laser.radius/2.)
        assert isclose(co2_laser.get_irr_r(hwhm), co2_laser.norm_coeff/2.)

    def test_laser_constructor_radial_grid(self):
        """Check that the radial grid for the beam profile is set correctly."""
        co2_laser = laser.GaussianBeam()
        assert co2_laser.r_grid[0] == 0
        assert co2_laser.r_grid[-1] == 2*co2_laser.radius
        assert len(co2_laser.r_grid) == 201

    def test_laser_constructor_radial_profile(self):
        """Check that the beam profile is set correctly.

        Note: The argument of the exponent in the Gaussian beam (i.e., -2*r^2/W^2 goes to 8 at
            r=2*W. This is why exp(-8) is used in one of these below. Also, the Half Width Full
            Maximum (HWFM) is equal to sqrt(2 ln(2))/2*W_0 or approximately 0.59*W_0 which occurs
            at index 59 (because W_0 is at index 100). This is the reason
            that index 59 is used in this test case.
        """
        co2_laser = laser.GaussianBeam()
        assert len(co2_laser.r_profile) == 201
        assert isclose(co2_laser.r_profile[0], co2_laser.norm_coeff)
        assert isclose(co2_laser.r_profile[-1], exp(-8)*co2_laser.norm_coeff)
        assert isclose(co2_laser.r_profile[59], co2_laser.norm_coeff/2., rel_tol=0.005)
