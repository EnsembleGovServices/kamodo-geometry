<!-- #region -->

# Kamodo Geometry

Geometric functions for advanced function composition.

## Motivation
Kamodo keeps a mapping between function signatures and specific plot types.
However, function authors may not be aware of the full context that their functions may be called, and this limits the kinds of plots available to end users.

This library contains a number of geometric functions that allow for much more flexibility in defining where functions should be evaluated. Each function contains many options not known to kamodo's plotting signatures, but which may be provisioned at run time.


## Examples


<!-- #endregion -->

```python
from kamodo import Kamodo
import numpy as np
```

```python
from geometry.space import cartesian
```

```python
cartesian
```

```python
cartesian.X(n=5)
```

```python
cartesian.X(n=5, space='log')
```

By default, the space argument is a dictionary specifying optional values

```python
from kamodo import get_defaults
get_defaults(cartesian.X)
```

This allows function parsers to determine what values are valid for this entry and expose these options to the end user. For example, `space` above would be dropdown allowing the user to specify between `linear` and `log` options.


It is up to the function to raise a `NotImplementedError` for invalid inputs. 

```python
try:
    cartesian.X(space='dirt')
except NotImplementedError as m:
    print(m)
```

## Plotting

```python
k = Kamodo(f='x**2-x-1')
```

Suppose we wish to evaluate `f` over a logarithmic space $x_i \in X$

```python
k.plot(f=dict(x=cartesian.X(n=10, space='log')))
```

This means the user can plot f in different spaces without registering a new function for `f` with alternate defaults each time.
