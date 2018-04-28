Variables
=========
All the variables are described here...

.. table:: *Table: Variables*
    
    +------------------------------------+------+----------------------------------+
    | Variable                           | Unit | Description                      |
    +====================================+======+==================================+
    | **Liquid Water Properties**                                                  |
    +------------------------------------+------+----------------------------------+
    | :math:`h_{\text{fg},s}`            | J/kg | Latent Heat of Vaporization      |
    +------------------------------------+------+----------------------------------+


Liquid Water Properties
^^^^^^^^^^^^^^^^^^^^^^^

**Latent Heat of Vaporization**, :math:`h_{\text{fg},s}` : the variable
:math:`h_{\text{fg},s}` represents the latent heat of vaporization at
:math:`T = T_s`, wehre :math:`T_s` is the surface temperature.

::

    >>> import chamber.props as props
    >>> props.hfgs(273.15)
    2500938
    >>> props.hfgs(290)
    2460974
    >>> props.hfgs(300)
    2437289
