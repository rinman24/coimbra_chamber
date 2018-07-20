Variables
=========
**This section is currently under construction!**

**To Do: Once the first IJHMT paper is submitted, we can fill out this section.**

*Some* the variables are described here...

.. table:: *Table: Variables*
    
    +------------------------------------+------------------+------------------------------------------+
    | Variable                           | Unit             | Description                              |
    +====================================+==================+==========================================+
    | **Film Properties**                                                                              |
    +------------------------------------+------------------+------------------------------------------+
    | :math:`c_{pm}`                     | J/kg humid air K | Mixture Specific Heat per Unit Humid Air |
    +------------------------------------+------------------+------------------------------------------+
    | **Liquid Water Properties**                                                                      |
    +------------------------------------+------------------+------------------------------------------+
    | :math:`h_{\text{fg},s}`            | J/kg             | Latent Heat of Vaporization              |
    +------------------------------------+------------------+------------------------------------------+

Film Properties
^^^^^^^^^^^^^^^

**Mixture Specific Heat per Unit Humid Air**, :math:`c_{pm}` : the variable
:math:`c_{pm}` represents the water-vapor/dry-air mixture specific heat per
unit humid air.

::

    >>> film_state = dict(P=101325, T=295, x1=0.01)
    1018.0

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
