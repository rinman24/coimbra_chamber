"""Constants for the UCSD Chamber Experiment."""

# ZnSe port parameters (From Spec Sheet)
D_PORT = 2.286e-2 # 2.286 cm         [X]
R_PORT = 1.143e-2 # 1.143 cm         [X]
A_PORT = 4.104e-4 # 4.104 cm^2       [X]

# Beam Parameters
"""
The cross-sectional area of the beam is chosen to be half of the area of the ZnSe aperature. As a
result, the radius of the beam will be smaller by a factor of 1/sqrt(2).
LAM  : wavelength of radiation
W_0  : beam radius at laser head
POW  : total power transmitted by the beam
Z_0  : Rayleigh length at the laser head
W_COL: beam radius after collimation
D_B  : diamter of the beam after collimation
A_CB : cross-sectional area of the beam after collimation
"""
LAM = 10.59e-6 # 10.59 microns       [X]
W_0 = 0.9e-3 # 0.9 mm                [X]
POW = 20 # 20 W                      [X]
Z_0 = 24.03e-2 # 24.03 cm            [X]
W_COL = 8.082e-3 # 8.082 mm          [X]
D_B = 1.616e-2 # 1.616 cm            [X]
A_CB = 2.052e-4 # 2.052 cm^2         [X]

# Stefan Tube Dimensions
D_IN_TUBE = 2.286e-2 # 2.286 cm      [X]
R_IN_TUBE = 1.143e-2 # 1.143 cm      [X]
A_C_TUBE = 4.104e-4 # 4.104 cm^2     [X]
D_OUT_TUBE = 3.4e-2 # 3.4 cm         [X]
R_OUT_TUBE = 1.7e-2 # 1.7 cm         [X]
H_IN_TUBE = 4.572e-2 # 4.572 cm      [X]
H_OUT_TUBE = 5.129e-2 # 5.129 cm     [X]
H_TUBE_BASE = 5.57e-3 # 5.57 mm      [X]

# Water Optical Properties at 10.59 microns
K_ABS_10P6 = 8.218e4 # 82,180 m^{-1} []
K_EXT_10P6 = 6.925e-2 # 0.06925      []
L_K_ABS = 1.22e-5 # 12 microns       []

