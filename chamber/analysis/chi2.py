"""
Module for performing chi-squared linear regression.

Functions
---------

- `chi2` -- perfroms a chi-squared linear regression.

"""

import math
import random

import matplotlib.pyplot as plt
import numpy as np
import scipy.stats

random.seed(10)


# --------------------------------------------------------------------------- #
# Metrics
# --------------------------------------------------------------------------- #


def _s(sigma, n):
    """Calculate S from Numerical Recipes 15.2.4 with constant sigma."""
    return 1/pow(sigma, 2) * n


def _s1(x, sigma):
    """Calculate S_x from Numerical Recipes 15.2.4 with constant sigma."""
    return sum(list(map(lambda x: x/pow(sigma, 2), x)))


def _sxx(x, sigma):
    """Calculate S_xx from Numerical Recipes 15.2.4 with constant sigma."""
    return sum(list(map(lambda x: pow(x, 2)/pow(sigma, 2), x)))


def _sxy(x, y, sigma):
    """Calculate S_xx from Numerical Recipes 15.2.4 with constant sigma."""
    return sum(list(map(lambda x, y: (x * y)/pow(sigma, 2), x, y)))


def _delta(s, sx, sxx):
    """Calculate Delta from Numerical Recipes 15.2.6 with constant sigma."""
    return s*sxx - pow(sx, 2)


def _a(sx, sy, sxx, sxy, delta):
    """Calculate a from Numerical Recipes 15.2.6 with constant sigma."""
    return (sxx*sy - sx*sxy)/delta


def _b(s, sx, sy, sxy, delta):
    """Calculate b from Numerical Recipes 15.2.6 with constant sigma."""
    return (s*sxy - sx*sy)/delta


def _sig_a(sxx, delta):
    """Calculate sigma_a from Numerical Recipes 15.2.9 with constant sigma."""
    return math.sqrt(sxx/delta)


def _sig_b(s, delta):
    """Calculate sigma_a from Numerical Recipes 15.2.9 with constant sigma."""
    return math.sqrt(s/delta)


def _chi2(x, y, a, b, sigma):
    """Calculate chi^2 from Numerical Recipes 15.2.2 with constant sigma."""
    return sum(list(map(lambda xi, yi: pow((yi-a-b*xi)/sigma, 2), x, y)))


# --------------------------------------------------------------------------- #
# Analysis
# --------------------------------------------------------------------------- #


def chi2(x, y, sigma, plot=False):
    """
    Use all of the helper function above to determine chi2 stats.

    .. todo:: chi2 docstring.

    """
    s_res = _s(sigma, len(x))
    sx_res = _s1(x, sigma)
    sy_res = _s1(y, sigma)
    sxx_res = _sxx(x, sigma)
    sxy_res = _sxy(x, y, sigma)
    delta_res = _delta(s_res, sx_res, sxx_res)
    a_res = _a(sx_res, sy_res, sxx_res, sxy_res, delta_res)
    b_res = _b(s_res, sx_res, sy_res, sxy_res, delta_res)
    sigma_a_res = _sig_a(sxx_res, delta_res)
    sigma_b_res = _sig_b(s_res, delta_res)
    chi2_res = _chi2(x, y, a_res, b_res, sigma)
    nu = len(x) - 2
    q_res = scipy.stats.chi2.sf(chi2_res, nu)
    if plot:
        plt.subplot(121)
        plt.errorbar(x, y, yerr=sigma, label='data', fmt='o', zorder=0)
        plt.plot(x, list(map(lambda x: a_res + b_res*x, x)),
                 label=r'$\chi^2$ fit', zorder=5)
        plt.xlabel('x')
        plt.ylabel('y')
        plt.legend()

        plt.subplot(122)
        chi = np.linspace(scipy.stats.chi2.ppf(0.0001, nu),
                          scipy.stats.chi2.ppf(0.9999, nu),
                          100)
        plt.plot(chi, scipy.stats.chi2.pdf(chi, nu), label=r'$\chi^2$ PDF')
        plt.axvline(x=chi2_res, ls='--', label=r'$\chi^2$')
        plt.ylim(bottom=0)
        plt.xlabel(r'$\chi^2$')
        plt.ylabel(r'$\chi^2$ Probability Density')
        plt.legend()

        plt.suptitle(r"$Q$ = {0:.4f}, $\nu$ = {1}".format(q_res, nu))

        plt.show()
    res = [a_res, sigma_a_res, b_res, sigma_b_res, chi2_res, q_res, nu]
    return res

# --------------------------------------------------------------------------- #
# Toy Data
# --------------------------------------------------------------------------- #


def _calc_bins(y, res):
    """Use the resolution to determine bins for the function's range."""
    y_max = max(y)
    y_min = min(y)
    bins = [y_min]

    while y_min < y_max:
        y_min += res
        bins.append(y_min)

    return bins


def add_steps(y, resolution):
    """Use bins to digitize y in to specified resolution.

    .. todo:: add_steps docstring or make function private.

    """
    bins = _calc_bins(y, resolution)
    idx = np.digitize(y, bins)
    return [bins[i-1] + 0.5*resolution for i in idx]


def add_noise(y, amp):
    """Use amp to add noise to _y attribute.

    .. todo:: add_noise docstring or make function private.

    """
    return list(map(lambda x: x + random.uniform(-1, 1)*amp, y))
