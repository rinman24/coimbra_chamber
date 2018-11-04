"""Unit testing of `film` module."""

import math

import pytest

from chamber.models import film


P_VALUE = 101325
TE_VALUE = 290
TDP_VALUE = 280
TS_VALUE = 285
TT_VALUE = 290


def test_use_rule():
    e_value = 1
    s_value = 0

    # Test e = 0 and s = 1 with '1/2'
    assert math.isclose(
        film.use_rule(e_value, s_value, '1/2'),
        1/2
    )

    # Test e = 0 and s = 1 with '1/3'
    assert math.isclose(
        film.use_rule(e_value, s_value, '1/3'),
        1/3
    )

    # Test raises ValueError
    with pytest.raises(ValueError) as err:
        film.use_rule(e_value, s_value, '1/4')
    err_msg = "'1/4' is not a valid rule; try '1/2' or '1/3'."
    assert err_msg in str(err.value)

    # Test temp_e = 300 and temp_s = 290 with '1/2'
    temp_e = 300
    temp_s = 290
    assert math.isclose(
        film.use_rule(temp_e, temp_s, '1/2'),
        295
    )

    # Test temp_e = 300 and temp_s = 290 with '1/3'
    assert math.isclose(
        film.use_rule(temp_e, temp_s, '1/3'),
        293.3333333333333
    )


def test_est_mix_props():
    # Test with ref = 'Mills' and rule = '1/2'
    film_props = film.est_mix_props(P_VALUE, TE_VALUE, TDP_VALUE, TS_VALUE,
                                'Mills', '1/2')

    assert math.isclose(film_props['c_pm'], 1019.9627505486458)
    assert math.isclose(film_props['rho_m'], 1.2229936606324967)
    assert math.isclose(film_props['k_m'], 0.025446947707731902)
    assert math.isclose(film_props['alpha_m'], 2.040317009201964e-05)
    assert math.isclose(film_props['d_12'], 2.3955520502741308e-05)

    # Test with ref = 'Mills' and rule = '1/3'
    film_props = film.est_mix_props(P_VALUE, TE_VALUE, TDP_VALUE, TS_VALUE,
                                'Mills', '1/3')

    assert math.isclose(film_props['c_pm'], 1020.7363637843752)
    assert math.isclose(film_props['rho_m'], 1.2262478476537964)
    assert math.isclose(film_props['k_m'], 0.025384761174818384)
    assert math.isclose(film_props['alpha_m'], 2.028355491502325e-05)
    assert math.isclose(film_props['d_12'], 2.3838525775468913e-05)

    # Test with ref = 'Marrero' and rule = '1/2'
    film_props = film.est_mix_props(P_VALUE, TE_VALUE, TDP_VALUE, TS_VALUE,
                                'Marrero', '1/2')

    assert math.isclose(film_props['c_pm'], 1019.9627505486458)
    assert math.isclose(film_props['rho_m'], 1.2229936606324967)
    assert math.isclose(film_props['k_m'], 0.025446947707731902)
    assert math.isclose(film_props['alpha_m'], 2.040317009201964e-05)
    assert math.isclose(film_props['d_12'], 2.323676676164935e-05)

    # Test with ref = 'Marrero' and rule = '1/3'
    film_props = film.est_mix_props(P_VALUE, TE_VALUE, TDP_VALUE, TS_VALUE,
                                'Marrero', '1/3')

    assert math.isclose(film_props['c_pm'], 1020.7363637843752)
    assert math.isclose(film_props['rho_m'], 1.2262478476537964)
    assert math.isclose(film_props['k_m'], 0.025384761174818384)
    assert math.isclose(film_props['alpha_m'], 2.028355491502325e-05)
    assert math.isclose(film_props['d_12'], 2.3097223037856368e-05)

    # Test raises ValueError for ref
    with pytest.raises(ValueError) as err:
        film.est_mix_props(P_VALUE, TE_VALUE, TDP_VALUE, TS_VALUE,
                       'C. F. M. Coimbra', '1/2')
    err_msg = (
        "'C. F. M. Coimbra' is not a valid ref; try 'Mills', 'Marrero', or "
        "'constant'."
        )
    assert err_msg in str(err.value)

    # Test raises ValueError for rule
    with pytest.raises(ValueError) as err:
        film.est_mix_props(P_VALUE, TE_VALUE, TDP_VALUE, TS_VALUE,
                       'Mills', 'Nu')
    err_msg = "'Nu' is not a valid rule; try '1/2' or '1/3'."
    assert err_msg in str(err.value)


def test_est_liq_props():
    # Test with rule = '1/2'
    liq_props = film.est_liq_props(TS_VALUE, TT_VALUE, '1/2')
    assert math.isclose(liq_props['c_pl'], 4189.82872258844)

    # Test with rule = '1/3'
    film_props = film.est_liq_props(TS_VALUE, TT_VALUE, '1/3')

    assert math.isclose(film_props['c_pl'], 4190.7955800723075)

    # Test raises ValueError for rule
    with pytest.raises(ValueError) as err:
        film.est_liq_props(TS_VALUE, TT_VALUE, 'No-Rules')
    err_msg = "'No-Rules' is not a valid rule; try '1/2' or '1/3'."
    assert err_msg in str(err.value)


def test_est_c_pm():
    # Test rule = '1/2'
    assert math.isclose(
        film.est_c_pm(P_VALUE, TE_VALUE, TDP_VALUE, TS_VALUE, '1/2'),
        1019.9627505486458
    )

    # Test rule = '1/3'
    assert math.isclose(
        film.est_c_pm(P_VALUE, TE_VALUE, TDP_VALUE, TS_VALUE, '1/3'),
        1020.7363637843752
    )

    # Test raises ValueError
    with pytest.raises(ValueError) as err:
        film.est_c_pm(P_VALUE, TE_VALUE, TDP_VALUE, TS_VALUE, '1/5')
    err_msg = "'1/5' is not a valid rule; try '1/2' or '1/3'."
    assert err_msg in str(err.value)


def test_est_rho_m():
    # Test rule = '1/2'
    assert math.isclose(
        film.est_rho_m(P_VALUE, TE_VALUE, TDP_VALUE, TS_VALUE, '1/2'),
        1.2229936606324967
    )

    # Test rule = '1/3'
    assert math.isclose(
        film.est_rho_m(P_VALUE, TE_VALUE, TDP_VALUE, TS_VALUE, '1/3'),
        1.2262478476537964
    )

    # Test raises ValueError
    with pytest.raises(ValueError) as err:
        film.est_rho_m(P_VALUE, TE_VALUE, TDP_VALUE, TS_VALUE, '24 Sep 1984')
    err_msg = "'24 Sep 1984' is not a valid rule; try '1/2' or '1/3'."
    assert err_msg in str(err.value)


def test_est_k_m():
    # Test rule = '1/2'
    assert math.isclose(
        film.est_k_m(P_VALUE, TE_VALUE, TDP_VALUE, TS_VALUE, '1/2'),
        0.025446947707731902
    )

    # Test rule = '1/3'
    assert math.isclose(
        film.est_k_m(P_VALUE, TE_VALUE, TDP_VALUE, TS_VALUE, '1/3'),
        0.025384761174818384
    )

    # Test raises ValueError
    with pytest.raises(ValueError) as err:
        film.est_k_m(P_VALUE, TE_VALUE, TDP_VALUE, TS_VALUE, '20 Mar 1987')
    err_msg = "'20 Mar 1987' is not a valid rule; try '1/2' or '1/3'."
    assert err_msg in str(err.value)


def test_est_alpha_m():
    # Test rule = '1/2'
    assert math.isclose(
        film.est_alpha_m(P_VALUE, TE_VALUE, TDP_VALUE, TS_VALUE, '1/2'),
        2.040317009201964e-05
    )

    # Test rule = '1/3'
    assert math.isclose(
        film.est_alpha_m(P_VALUE, TE_VALUE, TDP_VALUE, TS_VALUE, '1/3'),
        2.028355491502325e-05
    )

    # Test raises ValueError
    with pytest.raises(ValueError) as err:
        film.est_alpha_m(P_VALUE, TE_VALUE, TDP_VALUE, TS_VALUE, 'beta')
    err_msg = "'beta' is not a valid rule; try '1/2' or '1/3'."
    assert err_msg in str(err.value)


def test_est_d12():
    # Test ref = 'Mills' and rule = '1/2'
    assert math.isclose(
        film.est_d_12(P_VALUE, TE_VALUE, TDP_VALUE, TS_VALUE, '1/2', 'Mills'),
        2.3955520502741308e-05
    )

    # Test ref = 'Mills' and rule = '1/3'
    assert math.isclose(
        film.est_d_12(P_VALUE, TE_VALUE, TDP_VALUE, TS_VALUE, '1/3', 'Mills'),
        2.3838525775468913e-05
    )

    # Test ref = 'Marrero' and rule = '1/2'
    assert math.isclose(
        film.est_d_12(P_VALUE, TE_VALUE, TDP_VALUE, TS_VALUE, '1/2', 'Marrero'),
        2.323676676164935e-05
    )

    # Test ref = 'Marrerp' and rule = '1/3'
    assert math.isclose(
        film.est_d_12(P_VALUE, TE_VALUE, TDP_VALUE, TS_VALUE, '1/3', 'Marrero'),
        2.3097223037856368e-05
    )

    # Test raises ValueError for ref
    with pytest.raises(ValueError) as err:
        film.est_d_12(P_VALUE, TE_VALUE, TDP_VALUE, TS_VALUE,
                       '1/2', 'Inman et al.')
    err_msg = ("'Inman et al.' is not a valid ref; try 'Mills', 'Marrero', or "
               "'constant'.")
    assert err_msg in str(err.value)

    # Test raises ValueError for rule
    with pytest.raises(ValueError) as err:
        film.est_d_12(P_VALUE, TE_VALUE, TDP_VALUE, TS_VALUE, 'pi', 'Mills')
    err_msg = "'pi' is not a valid rule; try '1/2' or '1/3'."
    assert err_msg in str(err.value)


def test_est_c_pl():
    # Test rule = '1/2'
    assert math.isclose(
        film.est_c_pl(TS_VALUE, TT_VALUE, '1/2'),
        4189.82872258844
    )

    # Test rule = '1/3'
    assert math.isclose(
        film.est_c_pl(TS_VALUE, TT_VALUE, '1/3'),
        4190.7955800723075
    )

    # Test raises ValueError
    with pytest.raises(ValueError) as err:
        film.est_c_pl(TS_VALUE, TT_VALUE, 'gamma')
    err_msg = "'gamma' is not a valid rule; try '1/2' or '1/3'."
    assert err_msg in str(err.value)