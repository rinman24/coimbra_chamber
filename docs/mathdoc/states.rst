Film State
==========
In order to calculate thermophysical properties of the vapor mixture film, its
*state* must be specified. The `chamber` package uses a python dictionary to
with three keys  to represent the film's state. The keys are `P`, `T`, and `x1`
which represent the pressure [Pa], temperature [K], and water vapor mole
fraction.

See documentation for `chamber.models.film` for more information.
