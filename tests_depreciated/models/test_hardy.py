import math

import pytest

from chamber.models import hardy


def test__get_p_sat_water_ideal():
    """173 to 473"""
    assert math.isclose(hardy._get_p_sat_water_ideal(173),
                        0.0035124168637203535)
    assert math.isclose(hardy._get_p_sat_water_ideal(223), 6.3289928031397835)
    assert math.isclose(hardy._get_p_sat_water_ideal(273), 604.5834971866927)
    assert math.isclose(hardy._get_p_sat_water_ideal(323), 12261.037776936948)
    assert math.isclose(hardy._get_p_sat_water_ideal(373), 100876.03359085837)
    assert math.isclose(hardy._get_p_sat_water_ideal(423), 474801.61612936173)
    assert math.isclose(hardy._get_p_sat_water_ideal(473), 1561233.7377002165)


def test__get_p_sat_ice_ideal():
    """173 to 273"""
    assert math.isclose(hardy._get_p_sat_ice_ideal(173), 0.0013595772343005736)
    assert math.isclose(hardy._get_p_sat_ice_ideal(223), 3.863198938533606)
    assert math.isclose(hardy._get_p_sat_ice_ideal(273), 603.6458155647173)


def test__get_enh_alpha():
    # Ice
    assert math.isclose(
        hardy._get_enh_alpha(235), -0.0002821000421250053
        )
    assert math.isclose(
        hardy._get_enh_alpha(250), -0.00010349662500001855
        )
    assert math.isclose(
        hardy._get_enh_alpha(365), 0.011904734014412555
        )

    # Water
    assert math.isclose(
        hardy._get_enh_alpha(280), 0.0005695627168000872
        )
    assert math.isclose(
        hardy._get_enh_alpha(290), 0.000963162750099944
        )
    assert math.isclose(
        hardy._get_enh_alpha(300), 0.0014958583000000136
        )

    # 273 K
    assert math.isclose(
        hardy._get_enh_alpha(273), 0.0003569331704569856
        )
    assert math.isclose(
        hardy._get_enh_alpha(273.15), 0.000353626010163699
        )

    # Raise error
    with pytest.raises(ValueError) as err:
        hardy._get_enh_alpha(200)
    assert err.value.args[0] == "`t_in` must be between 223.15 K and 373.15 K."


def test__get_enh_beta():
    # Ice
    assert math.isclose(hardy._get_enh_beta(235), 8.081338063035154e-07)
    assert math.isclose(hardy._get_enh_beta(250), 3.34037535684878e-06)
    assert math.isclose(hardy._get_enh_beta(265), 1.1658965160489346e-05)

    # Water
    assert math.isclose(hardy._get_enh_beta(280), 3.2407759234858634e-05)
    assert math.isclose(hardy._get_enh_beta(290), 5.761508492677925e-05)
    assert math.isclose(hardy._get_enh_beta(300), 9.798783888539943e-05)

    # 273 K
    assert math.isclose(hardy._get_enh_beta(273), 2.1420566119463687e-05)
    assert math.isclose(hardy._get_enh_beta(273.15), 2.1257528035606742e-05)

    # Raise error
    with pytest.raises(ValueError) as err:
        hardy._get_enh_beta(400)
    assert err.value.args[0] == "`t_in` must be between 223.15 K and 373.15 K."


def test__get_enh_fact():
    # ----------------------------------------------------------------------- #
    # 1 atm
    # ----------------------------------------------------------------------- #
    p = 101325

    # Ice
    assert math.isclose(hardy._get_enh_fact(p, 235), 1.004911524525183)
    assert math.isclose(hardy._get_enh_fact(p, 250), 1.0043558345725534)
    assert math.isclose(hardy._get_enh_fact(p, 265), 1.0040107321092107)

    # Water
    assert math.isclose(hardy._get_enh_fact(p, 280), 1.0038499176571687)
    assert math.isclose(hardy._get_enh_fact(p, 290), 1.003935677395981)
    assert math.isclose(hardy._get_enh_fact(p, 300), 1.0041615041719245)
    assert math.isclose(hardy._get_enh_fact(p, 373), 1.0000718143977247)

    # 273 K
    assert math.isclose(hardy._get_enh_fact(p, 273), 1.0039366648046184)
    assert math.isclose(hardy._get_enh_fact(p, 273.15), 1.003861680225293)

    # ----------------------------------------------------------------------- #
    # 0.67 atm
    # ----------------------------------------------------------------------- #
    p = 101325*0.67

    # Ice
    assert math.isclose(hardy._get_enh_fact(p, 235), 1.0031944344175807)
    assert math.isclose(hardy._get_enh_fact(p, 250), 1.002881021342391)
    assert math.isclose(hardy._get_enh_fact(p, 265), 1.0027318353085357)

    # Water
    assert math.isclose(hardy._get_enh_fact(p, 280), 1.002750944693484)
    assert math.isclose(hardy._get_enh_fact(p, 290), 1.002919801994187)
    assert math.isclose(hardy._get_enh_fact(p, 300), 1.003205899463673)
    assert math.isclose(hardy._get_enh_fact(p, 373), 0.9924377393985329)

    # 273 K
    assert math.isclose(hardy._get_enh_fact(p, 273), 1.0027451184407103)
    assert math.isclose(hardy._get_enh_fact(p, 273.15), 1.002693891894866)

    # ----------------------------------------------------------------------- #
    # 0.33 atm
    # ----------------------------------------------------------------------- #
    p = 101325*0.33

    # Ice
    assert math.isclose(hardy._get_enh_fact(p, 235), 1.0014284253099317)
    assert math.isclose(hardy._get_enh_fact(p, 250), 1.001363861938361)
    assert math.isclose(hardy._get_enh_fact(p, 265), 1.0014154109784066)

    # Water
    assert math.isclose(hardy._get_enh_fact(p, 280), 1.001614174710464)
    assert math.isclose(hardy._get_enh_fact(p, 290), 1.0018553792868357)
    assert math.isclose(hardy._get_enh_fact(p, 300), 1.002168373789947)
    assert math.isclose(hardy._get_enh_fact(p, 373), 0.970162753563328)

    # 273 K
    assert math.isclose(hardy._get_enh_fact(p, 273), 1.001516749541024)
    assert math.isclose(hardy._get_enh_fact(p, 273.15), 1.0014899358177423)

    # Raise error
    with pytest.raises(ValueError) as err:
        hardy._get_enh_fact(p, 200)
    assert err.value.args[0] == "`t_in` must be between 223.15 K and 373.15 K."


def test_get_p_sat():
    # ----------------------------------------------------------------------- #
    # 1 atm
    # ----------------------------------------------------------------------- #
    p = 101325

    # Ice
    assert math.isclose(hardy.get_p_sat(p, 235), 15.87813860915064)
    assert math.isclose(hardy.get_p_sat(p, 250), 76.33674778018978)
    assert math.isclose(hardy.get_p_sat(p, 265), 307.1373245873579)

    # Water
    assert math.isclose(hardy.get_p_sat(p, 280), 995.5941863168321)
    assert math.isclose(hardy.get_p_sat(p, 290), 1927.4871654892165)
    assert math.isclose(hardy.get_p_sat(p, 300), 3551.542766492522)
    assert math.isclose(hardy.get_p_sat(p, 373), 100883.27794245555)

    # 273 K
    assert math.isclose(hardy.get_p_sat(p, 273), 606.0221668013061)
    assert math.isclose(hardy.get_p_sat(p, 273.15), 613.5732195082734)

    # ----------------------------------------------------------------------- #
    # 0.67 atm
    # ----------------------------------------------------------------------- #
    p = 101325*0.67

    # Ice
    assert math.isclose(hardy.get_p_sat(p, 235), 15.851007668697159,)
    assert math.isclose(hardy.get_p_sat(p, 250), 76.22465359832873)
    assert math.isclose(hardy.get_p_sat(p, 265), 306.74609675560214)

    # Water
    assert math.isclose(hardy.get_p_sat(p, 280), 994.504251383015)
    assert math.isclose(hardy.get_p_sat(p, 290), 1925.5367548774796)
    assert math.isclose(hardy.get_p_sat(p, 300), 3548.162960579711)
    assert math.isclose(hardy.get_p_sat(p, 373), 100113.18273640194)

    # 273 K
    assert math.isclose(hardy.get_p_sat(p, 273), 605.3028948246816)
    assert math.isclose(hardy.get_p_sat(p, 273.15), 612.8594522037544)

    # ----------------------------------------------------------------------- #
    # 0.33 atm
    # ----------------------------------------------------------------------- #
    p = 101325*0.33

    # Ice
    assert math.isclose(hardy.get_p_sat(p, 235), 15.823103781925115)
    assert math.isclose(hardy.get_p_sat(p, 250), 76.10934086674382)
    assert math.isclose(hardy.get_p_sat(p, 265), 306.34338886230285)

    # Water
    assert math.isclose(hardy.get_p_sat(p, 280), 993.3768302751711)
    assert math.isclose(hardy.get_p_sat(p, 290), 1923.49313679191)
    assert math.isclose(hardy.get_p_sat(p, 300), 3544.4934146090054)
    assert math.isclose(hardy.get_p_sat(p, 373), 97866.17051705392)

    # 273 K
    assert math.isclose(hardy.get_p_sat(p, 273), 604.5613950784161)
    assert math.isclose(hardy.get_p_sat(p, 273.15), 612.1235787055035,)
