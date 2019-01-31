"""Constants used for Spalding engine unit testing."""

import uncertainties as un

mass = 0.099
press = 101325
amb_temp = 290
dew_point = 280
ref = 'Mills'
rule = '1/2'

spald_input = dict(
    m=mass, p=press, t_e=amb_temp, t_dp=dew_point,
    ref=ref, rule=rule)

exp_state = dict(
    L=un.ufloat(0.04351613825556731, 0.0012399392152624728),
    P=un.ufloat(101325.0, 151.9875),
    T=un.ufloat(amb_temp, 0.2),
    T_dp=un.ufloat(280, 0.2),
    )

initial_s_state = dict(
    h=0,
    h_fg=2460974.1659213207,
    m_1=0.011919754919993641,
    T=amb_temp,
    )

initial_u_state = dict(
    T=amb_temp,
    h=-2460974.1659213207,
    )

initial_liq_props = dict(
    c_p=4186.928150136838,
    T=amb_temp,
    )

initial_t_state = dict(
    T=amb_temp,
    h=-2460974.1659213207,
    )

initial_film_props = dict(
    T=290,
    m_1=0.00902269579164411,
    c_p=1023.2052734002779,
    rho=1.2111324605139007,
    k=0.025631496411099592,
    alpha=2.068328650706946e-05,
    D_12=2.4306504684558495e-05,
    nu=1.4842910873836943e-05,
    M=28.865210503777288,
    beta=0.0034482758620689655,
    gamma_1=0.4972928938519298,
    )

initial_e_state = dict(
    m_1=.0061357476021502095,
    T=amb_temp,
    h=0,
    c_p=1017.6419108408694,
    )

properties = [
    'film_guide', 'exp_state', 's_state', 'u_state', 'liq_props', 't_state',
    'film_props',
    ]

updated_s_state = dict(
    h=0,
    h_fg=2464523.5469389744,
    m_1=0.010823709872538528,
    T=288.5,
    )

updated_u_state = dict(
    T=288.5,
    h=-2464523.5469389744,
    )

updated_liq_props = dict(
    c_p=4187.904140394711,
    T=289,
    )

updated_t_state = dict(
    T=amb_temp,
    h=-2458241.690728382,
    )

updated_film_props = dict(
    T=289,
    m_1=0.009258101386974069,
    c_p=1023.6375283508754,
    rho=1.2151650870711066,
    k=0.02555730048179153,
    alpha=2.0546293907620422e-05,
    D_12=2.348669655145598e-05,
    nu=1.4752460529166174e-05,
    M=28.86263304791402,
    beta=0.0034602076124567475,
    gamma_1=0.495524846597762,
    )

updated_e_state = dict(
    m_1=.0061357476021502095,
    T=amb_temp,
    h=1526.462866261304,
    c_p=1017.6419108408694,
    )

solution = dict(
    mddp=un.ufloat(3.284808446197291e-06, 4.738115733994133e-08),
    T_s=un.ufloat(288.67153957333227, 0.21853985929396913),
    q_cu=un.ufloat(0.01827344575501605, 0.0005157964229627193),
    q_rs=un.ufloat(7.2984134656147, 0.08623041453291957),
    m_1s=un.ufloat(0.010944358137168323, 0.0001387447912517964),
    m_1e=un.ufloat(0.0061357476021502095, 7.584305580521714e-05),
    B_m1=un.ufloat(0.004861820033452959, 6.428880743755867e-05),
    B_h=un.ufloat(0.005711779013247194, 7.571770613666942e-05),
    g_m1=un.ufloat(0.0006756334919012533, 1.8435814500340785e-05),
    g_h=un.ufloat(0.000575093756004725, 1.571075402144169e-05),
    Sh_L=un.ufloat(1.0000000002514167, 7.253420086783535e-11),
    Nu_L=un.ufloat(0.999999999945239, 1.0491696400549699e-10),
    Gr_mR=un.ufloat(439.0791958657675, 5.869469438756312),
    Gr_hR=un.ufloat(-695.7494257654488, 9.937542697171466),
    Gr_R=un.ufloat(439.0791958657675, 5.869469438756312),
    rho=un.ufloat(1.214274984282096, 0.0008625274923872439),
    D_12=un.ufloat(2.4212769608901406e-05, 6.793023540863866e-09),
    alpha=un.ufloat(2.0609713385787443e-05, 6.457597103448224e-09),
    )
