"""Unit tests (pytest) for the chi2 module."""

import math
import os

import numpy as np
import pandas as pd
import pytest

from chamber.analysis import chi2

REF = os.path.join('tests', 'analysis', 'csv_test_files')
DF11 = pd.read_csv(os.path.join(REF, 'points11.csv'))
DF51 = pd.read_csv(os.path.join(REF, 'points51.csv'))
DF101 = pd.read_csv(os.path.join(REF, 'points101.csv'))
DF501 = pd.read_csv(os.path.join(REF, 'points501.csv'))
DF1001 = pd.read_csv(os.path.join(REF, 'points1001.csv'))
DF5001 = pd.read_csv(os.path.join(REF, 'points5001.csv'))
DF10001 = pd.read_csv(os.path.join(REF, 'points10001.csv'))

X = [i/10 for i in range(0, 11)]
Y = list(reversed(X))

YP06 = chi2.add_steps(Y, 0.06)
YP2 = chi2.add_steps(Y, 0.2)
YP45 = chi2.add_steps(Y, 0.45)
YP1 = chi2.add_noise(Y, 0.1)
YP25 = chi2.add_noise(Y, 0.25)
YP5 = chi2.add_noise(Y, 0.5)
YP75 = chi2.add_noise(Y, 0.75)

# Check if the test is being run in Continuous Integration or not
if os.getenv('CI'):
    PLOT = False
else:
    PLOT = True


class TestChi2_0p06(object):
    """Unit testing of the chi2 module."""

    sigma = 0.06

    def test__s(self):
        """Test _s."""
        s = chi2._s(self.sigma, len(X))
        assert math.isclose(s, 3055.5555555555557)

    def test__sx(self):
        """Test _s1."""
        sx = chi2._s1(X, self.sigma)
        assert math.isclose(sx, 1527.7777777777778)

    def test__sy(self):
        """Test _s1."""
        sy = chi2._s1(YP06, self.sigma)
        assert math.isclose(sy, 1525)

    def test__sxx(self):
        """Test _sxx."""
        sxx = chi2._sxx(X, self.sigma)
        assert math.isclose(sxx, 1069.4444444444446)

    def test__sxy(self):
        """Test _sxy."""
        sxy = chi2._sxy(X, YP06, self.sigma)
        assert math.isclose(sxy, 467.5)

    def test__delta(self):
        """Test _delta."""
        s = chi2._s(self.sigma, len(X))
        sx = chi2._s1(X, self.sigma)
        sxx = chi2._sxx(X, self.sigma)
        delta = chi2._delta(s, sx, sxx)
        assert math.isclose(delta, 933641.9753086423)

    def test__a__b(self):
        """Test _a and _b."""
        s = chi2._s(self.sigma, len(X))
        sx = chi2._s1(X, self.sigma)
        sy = chi2._s1(YP06, self.sigma)
        sxx = chi2._sxx(X, self.sigma)
        sxy = chi2._sxy(X, YP06, self.sigma)
        delta = chi2._delta(s, sx, sxx)
        a = chi2._a(sx, sy, sxx, sxy, delta)
        b = chi2._b(s, sx, sy, sxy, delta)
        assert math.isclose(a, 0.981818181818182)
        assert math.isclose(b, -0.9654545454545456)

    def test__sig_a_b(self):
        """Test _sig_a and _sig_b."""
        s = chi2._s(self.sigma, len(X))
        sx = chi2._s1(X, self.sigma)
        sxx = chi2._sxx(X, self.sigma)
        delta = chi2._delta(s, sx, sxx)
        sigma_a = chi2._sig_a(sxx, delta)
        sigma_b = chi2._sig_b(s, delta)
        assert math.isclose(sigma_a, 0.03384456448906597)
        assert math.isclose(sigma_b, 0.05720775535473553)

    def test_chi2(self):
        """Test chi2."""
        s = chi2._s(self.sigma, len(X))
        sx = chi2._s1(X, self.sigma)
        sy = chi2._s1(YP06, self.sigma)
        sxx = chi2._sxx(X, self.sigma)
        sxy = chi2._sxy(X, YP06, self.sigma)
        delta = chi2._delta(s, sx, sxx)
        a = chi2._a(sx, sy, sxx, sxy, delta)
        b = chi2._b(s, sx, sy, sxy, delta)
        chi_sq = chi2._chi2(X, YP06, a, b, self.sigma)
        assert math.isclose(chi_sq, 0.827272727272728)

    def test_run_chi2_noplot(self):
        """Test chi2 with plot=false."""
        res = chi2.chi2(X, YP06, self.sigma)
        assert math.isclose(res[0], 0.981818181818182)
        assert math.isclose(res[1], 0.03384456448906597)
        assert math.isclose(res[2], -0.9654545454545456)
        assert math.isclose(res[3], 0.05720775535473553)
        assert math.isclose(res[4], 0.827272727272728)
        assert math.isclose(res[5], 0.9997430671082018)

    def test_run_chi2_plot(self):
        """Test chi2 with plot set by CI detection."""
        res = chi2.chi2(X, YP06, self.sigma, plot=PLOT)
        assert math.isclose(res[0], 0.981818181818182)
        assert math.isclose(res[1], 0.03384456448906597)
        assert math.isclose(res[2], -0.9654545454545456)
        assert math.isclose(res[3], 0.05720775535473553)
        assert math.isclose(res[4], 0.827272727272728)
        assert math.isclose(res[5], 0.9997430671082018)


class TestChi2_0p2(object):
    """Unit testing of the chi2 module."""

    sigma = 0.2

    def test__s(self):
        """Test _s."""
        print(self.sigma)
        s = chi2._s(self.sigma, len(X))
        assert math.isclose(s, 274.99999999999994)

    def test__sx(self):
        """Test _s1."""
        sx = chi2._s1(X, self.sigma)
        assert math.isclose(sx, 137.49999999999997)

    def test__sy(self):
        """Test _s1."""
        sy = chi2._s1(YP2, self.sigma)
        assert math.isclose(sy, 147.5)

    def test__sxx(self):
        """Test _sxx."""
        sxx = chi2._sxx(X, self.sigma)
        assert math.isclose(sxx, 96.25)

    def test_sxy(self):
        """Test _sxy."""
        sxy = chi2._sxy(X, YP2, self.sigma)
        assert math.isclose(sxy, 46.75)

    def test_delta(self):
        """Test _delta."""
        s = chi2._s(self.sigma, len(X))
        sx = chi2._s1(X, self.sigma)
        sxx = chi2._sxx(X, self.sigma)
        delta = chi2._delta(s, sx, sxx)
        assert math.isclose(delta, 7562.5)

    def test__a__b(self):
        """Test _a and _b."""
        s = chi2._s(self.sigma, len(X))
        sx = chi2._s1(X, self.sigma)
        sy = chi2._s1(YP2, self.sigma)
        sxx = chi2._sxx(X, self.sigma)
        sxy = chi2._sxy(X, YP2, self.sigma)
        delta = chi2._delta(s, sx, sxx)
        a = chi2._a(sx, sy, sxx, sxy, delta)
        b = chi2._b(s, sx, sy, sxy, delta)
        assert math.isclose(a, 1.0272727272727273)
        assert math.isclose(b, -0.9818181818181816)

    def test__sig_a_b(self):
        """Test _sig_a and _sig_b."""
        s = chi2._s(self.sigma, len(X))
        sx = chi2._s1(X, self.sigma)
        sxx = chi2._sxx(X, self.sigma)
        delta = chi2._delta(s, sx, sxx)
        sigma_a = chi2._sig_a(sxx, delta)
        sigma_b = chi2._sig_b(s, delta)
        assert math.isclose(sigma_a, 0.11281521496355325)
        assert math.isclose(sigma_b, 0.19069251784911845)

    def test_chi2(self):
        """Test chi2."""
        s = chi2._s(self.sigma, len(X))
        sx = chi2._s1(X, self.sigma)
        sy = chi2._s1(YP2, self.sigma)
        sxx = chi2._sxx(X, self.sigma)
        sxy = chi2._sxy(X, YP2, self.sigma)
        delta = chi2._delta(s, sx, sxx)
        a = chi2._a(sx, sy, sxx, sxy, delta)
        b = chi2._b(s, sx, sy, sxy, delta)
        chi_sq = chi2._chi2(X, YP2, a, b, self.sigma)
        assert math.isclose(chi_sq, 1.1272727272727274)

    def test_run_chi2_noplot(self):
        """Test chi2 with plot=false."""
        res = chi2.chi2(X, YP2, self.sigma)
        assert math.isclose(res[0], 1.0272727272727273)
        assert math.isclose(res[1], 0.11281521496355325)
        assert math.isclose(res[2], -0.9818181818181816)
        assert math.isclose(res[3], 0.19069251784911845)
        assert math.isclose(res[4], 1.1272727272727274)
        assert math.isclose(res[5], 0.999083798853131)

    def test_run_chi2_plot(self):
        """Test chi2 with plot set by CI detection."""
        res = chi2.chi2(X, YP2, self.sigma, plot=PLOT)
        assert math.isclose(res[0], 1.0272727272727273)
        assert math.isclose(res[1], 0.11281521496355325)
        assert math.isclose(res[2], -0.9818181818181816)
        assert math.isclose(res[3], 0.19069251784911845)
        assert math.isclose(res[4], 1.1272727272727274)
        assert math.isclose(res[5], 0.999083798853131)


class TestChi2_0p45(object):
    """Unit testing of the chi2 module."""

    sigma = 0.45

    def test_run_chi2_plot(self):
        """Test chi2."""
        res = chi2.chi2(X, YP45, self.sigma, plot=PLOT)
        assert math.isclose(res[0], 1.0431818181818182)
        assert math.isclose(res[1], 0.2538342336679948)
        assert math.isclose(res[2], -0.9818181818181816)
        assert math.isclose(res[3], 0.4290581651605166)
        assert math.isclose(res[4], 0.9454545454545453)
        assert math.isclose(res[5], 0.9995532579195288)


class TestChi2_0p1(object):
    """Unit testing of the chi2 module."""

    sigma = 0.1

    def test_run_chi2_plot(self):
        """Test chi2."""
        res = chi2.chi2(X, YP1, self.sigma, plot=PLOT)
        assert math.isclose(res[0], 1.0191128267746108)
        assert math.isclose(res[1], 0.056407607481776624)
        assert math.isclose(res[2], -1.0442790264620143)
        assert math.isclose(res[3], 0.09534625892455922)
        assert math.isclose(res[4], 1.9226552415383538)
        assert math.isclose(res[5], 0.9926324308300408)


class TestChi2_0p25(object):
    """Unit testing of the chi2 module."""

    sigma = 0.25

    def test_run_chi2_plot(self):
        """Test chi2."""
        res = chi2.chi2(X, YP25, self.sigma, plot=PLOT)
        assert math.isclose(res[0], 1.0989726209350092)
        assert math.isclose(res[1], 0.14101901870444156)
        assert math.isclose(res[2], -1.0977625200576255)
        assert math.isclose(res[3], 0.23836564731139806)
        assert math.isclose(res[4], 3.2040118065476277)
        assert math.isclose(res[5], 0.9556541198996903)


class TestChi2_0p5(object):
    """Unit testing of the chi2 module."""

    sigma = 0.5

    def test_run_chi2_plot(self):
        """Test chi2."""
        res = chi2.chi2(X, YP5, self.sigma, plot=PLOT)
        assert math.isclose(res[0], 1.1188586115644354)
        assert math.isclose(res[1], 0.2820380374088831)
        assert math.isclose(res[2], -1.281673418078595)
        assert math.isclose(res[3], 0.4767312946227961)
        assert math.isclose(res[4], 5.674581303089316)
        assert math.isclose(res[5], 0.7719937978528024)


class TestChi2_0p75(object):
    """Unit testing of the chi2 module."""

    sigma = 0.75

    def test_run_chi2_plot(self):
        """Test chi2."""
        res = chi2.chi2(X, YP75, self.sigma, plot=PLOT)
        assert math.isclose(res[0], 1.1847672848790627)
        assert math.isclose(res[1], 0.4230570561133248)
        assert math.isclose(res[2], -1.6363451730845522)
        assert math.isclose(res[3], 0.7150969419341944)
        assert math.isclose(res[4], 2.581546572691533)
        assert math.isclose(res[5], 0.9786093749846231)


class TestChi2_0p75_0p25(object):
    """Unit testing of the chi2 module."""

    sigma = 0.25

    def test_run_chi2_plot(self):
        """Test chi2."""
        res = chi2.chi2(X, YP75, self.sigma, plot=PLOT)
        assert math.isclose(res[0], 1.1847672848790618)
        assert math.isclose(res[1], 0.14101901870444156)
        assert math.isclose(res[2], -1.6363451730845509)
        assert math.isclose(res[3], 0.23836564731139806)
        assert math.isclose(res[4], 23.2339191542238)
        assert math.isclose(res[5], 0.0056918026170632175)


class TestChi2_0p45_0p1(object):
    """Unit testing of the chi2 module."""

    sigma = 0.1

    def test_run_chi2_plot(self):
        """Test chi2."""
        res = chi2.chi2(X, YP45, self.sigma, plot=PLOT)
        assert math.isclose(res[0], 1.043181818181818)
        assert math.isclose(res[1], 0.056407607481776624)
        assert math.isclose(res[2], -0.9818181818181816)
        assert math.isclose(res[3], 0.09534625892455922)
        assert math.isclose(res[4], 19.145454545454548)
        assert math.isclose(res[5], 0.023984142487247596)


class TestChi2_0p45_0p045(object):
    """Unit testing of the chi2 module."""

    sigma = 0.045

    def test_run_chi2_plot(self):
        """Test chi2."""
        res = chi2.chi2(X, YP45, self.sigma, plot=PLOT)
        assert math.isclose(res[0], 1.0431818181818193)
        assert math.isclose(res[1], 0.025383423366799482)
        assert math.isclose(res[2], -0.9818181818181835)
        assert math.isclose(res[3], 0.04290581651605166)
        assert math.isclose(res[4], 94.54545454545455)
        assert math.isclose(res[5], 1.9854513069227152e-16)


class TestChi2_p11(object):
    """Unit testing of the chi2 module."""

    sigma = 4e-8

    def test_run_chi2_plot(self):
        """Test chi2."""
        res = chi2.chi2(DF11.index, DF11.Mass, self.sigma, plot=PLOT)
        assert math.isclose(res[0], 0.09898892227272728)
        assert math.isclose(res[1], 2.256304299271065e-08)
        assert math.isclose(res[2], -1.0454545449254118e-08)
        assert math.isclose(res[3], 3.81385035698237e-09)
        assert math.isclose(res[4], 2.2357954553695047)
        assert math.isclose(res[5], 0.9871665124539309)


class TestChi2_p51(object):
    """Unit testing of the chi2 module."""

    sigma = 4e-8

    def test_run_chi2_plot(self):
        """Test chi2."""
        res = chi2.chi2(DF51.index, DF51.Mass, self.sigma, plot=PLOT)
        assert math.isclose(res[0], 0.09898901563348429)
        assert math.isclose(res[1], 1.1039487604783525e-08)
        assert math.isclose(res[2], -6.860633486941241e-09)
        assert math.isclose(res[3], 3.805211953235955e-10)
        assert math.isclose(res[4], 17.83166855192995)
        assert math.isclose(res[5], 0.9999874136465203)


class TestChi2_p101(object):
    """Unit testing of the chi2 module."""

    sigma = 4e-8

    def test_run_chi2_plot(self):
        """Test chi2."""
        res = chi2.chi2(DF101.index, DF101.Mass, self.sigma, plot=PLOT)
        assert math.isclose(res[0], 0.09898911309260354)
        assert math.isclose(res[1], 7.90154913558044e-09)
        assert math.isclose(res[2], -5.4064065262730515e-09)
        assert math.isclose(res[3], 1.3651797622815265e-10)
        assert math.isclose(res[4], 39.55889924420013)
        assert math.isclose(res[5], 0.9999999857906134)


class TestChi2_p501(object):
    """Unit testing of the chi2 module."""

    sigma = 4e-8

    def test_run_chi2_plot(self):
        """Test chi2."""
        res = chi2.chi2(DF501.index, DF501.Mass, self.sigma, plot=PLOT)
        assert math.isclose(res[0], 0.09899027903905232)
        assert math.isclose(res[1], 3.568792572732848e-09)
        assert math.isclose(res[2], -5.7219047123584375e-09)
        assert math.isclose(res[3], 1.2356483417375422e-11)
        assert math.isclose(res[4], 156.05728207857018)
        assert math.isclose(res[5], 1)


class TestChi2_p1001(object):
    """Unit testing of the chi2 module."""

    sigma = 4e-8

    def test_run_chi2_plot(self):
        """Test chi2."""
        res = chi2.chi2(DF1001.index, DF1001.Mass, self.sigma, plot=PLOT)
        assert math.isclose(res[0], 0.09899174702441146)
        assert math.isclose(res[1], 2.52666482275547e-09)
        assert math.isclose(res[2], -5.7923705010799915e-09)
        assert math.isclose(res[3], 4.375218178856168e-12)
        assert math.isclose(res[4], 394.1311094571072)
        assert math.isclose(res[5], 1)


class TestChi2_p5001(object):
    """Unit testing of the chi2 module."""

    sigma = 4e-8

    def test_run_chi2_plot(self):
        """Test chi2."""
        res = chi2.chi2(DF5001.index, DF5001.Mass, self.sigma, plot=PLOT)
        assert math.isclose(res[0], 0.09900337269225801)
        assert math.isclose(res[1], 1.1310880962516921e-09)
        assert math.isclose(res[2], -5.789575205713899e-09)
        assert math.isclose(res[3], 3.9180082055755587e-13)
        assert math.isclose(res[4], 13673.272478061841)
        assert math.isclose(res[5], 0)


class TestChi2_p10001(object):
    """Unit testing of the chi2 module."""

    sigma = 4e-8

    def test_run_chi2_plot(self):
        """Test chi2."""
        res = chi2.chi2(DF10001.index, DF10001.Mass, self.sigma, plot=PLOT)
        print('a', res[0], res[1])
        print('b', res[2], res[3])
        print('chi2', res[4], res[5])
        assert math.isclose(res[0], 0.09901806256496763)
        assert math.isclose(res[1], 7.99900015747367e-10)
        assert math.isclose(res[2], -5.794755770688049e-09)
        assert math.isclose(res[3], 1.3854328328616986e-13)
        assert math.isclose(res[4], 324347.8295700301)
        assert math.isclose(res[5], 0)


class TestDataset(object):
    """Unit testing of the Dataset module."""

    def test_calc_bins_0p06(self):
        """Test _calc_bins."""
        res = 0.06
        bins = chi2._calc_bins(Y, res)
        assert len(bins) == 18
        b = 0
        for i in bins:
            assert math.isclose(i, b)
            b += res

    def test_calc_bins_0p2(self):
        """Test _calc_bins."""
        res = 0.2
        bins = chi2._calc_bins(Y, res)
        assert len(bins) == 6
        b = 0
        for i in bins:
            assert math.isclose(i, b)
            b += res

    def test_calc_bins_0p45(self):
        """Test _calc_bins."""
        res = 0.45
        bins = chi2._calc_bins(Y, res)
        assert len(bins) == 4
        b = 0
        for i in bins:
            assert math.isclose(i, b)
            b += res

    def test_calc_bins_5(self):
        """Test _calc_bins."""
        res = 5
        bins = chi2._calc_bins(Y, res)
        assert len(bins) == 2
        b = 0
        for i in bins:
            assert math.isclose(i, b)
            b += res

    def test_add_steps_0p06(self):
        """Test add_stepss."""
        res = 0.06
        y_new = chi2.add_steps(Y, res)
        assert math.isclose(y_new[0], 0.99)
        assert math.isclose(y_new[5], 0.51)
        assert math.isclose(y_new[-1], 0.03)

    def test_add_steps_0p02(self):
        """Test add_stepss."""
        res = 0.2
        y_new = chi2.add_steps(Y, res)
        assert math.isclose(y_new[0], 1.1)
        assert math.isclose(y_new[5], 0.5)
        assert math.isclose(y_new[-1], 0.1)

    def test_add_steps_0p45(self):
        """Test add_stepss."""
        res = 0.45
        y_new = chi2.add_steps(Y, res)
        assert math.isclose(y_new[0], 1.125)
        assert math.isclose(y_new[5], 0.675)
        assert math.isclose(y_new[-1], 0.225)

    def test_add_steps_5(self):
        """Test add_steps."""
        res = 5
        y_new = chi2.add_steps(Y, res)
        assert math.isclose(y_new[0], 2.5)
        assert math.isclose(y_new[5], 2.5)
        assert math.isclose(y_new[-1], 2.5)

    def test_add_noise_0p1(self):
        """Test add_noise."""
        amp = 0.1
        y_new = chi2.add_noise(Y, amp)
        assert math.isclose(y_new[0], 0.9993206997233096)
        assert math.isclose(y_new[5], 0.4299376269942803)
        assert math.isclose(y_new[-1], 0.05510254021456558)

    def test_add_noise_0p25(self):
        """Test add_noise."""
        amp = 0.25
        y_new = chi2.add_noise(Y, amp)
        assert math.isclose(y_new[0], 0.7983029165921763)
        assert math.isclose(y_new[5], 0.4570404158741506)
        assert math.isclose(y_new[-1], -0.19025874783461144)

    def test_add_noise_0p5(self):
        """Test add_noise."""
        amp = 0.5
        y_new = chi2.add_noise(Y, amp)
        assert math.isclose(y_new[0], 0.9557348586810382)
        assert math.isclose(y_new[5], 0.48013339022434753)
        assert math.isclose(y_new[-1], -0.16834277736450454)

    def test_add_noise_0p75(self):
        """Test add_noise."""
        amp = 0.75
        y_new = chi2.add_noise(Y, amp)
        assert math.isclose(y_new[0], 0.7291348566408009)
        assert math.isclose(y_new[5], 1.0543183180961042)
        assert math.isclose(y_new[-1], 0.030164541482119278)
