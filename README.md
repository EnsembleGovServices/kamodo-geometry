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

$$X{\left(x_{1},x_{2},n,space,base \right)} = \lambda{\left(x_{1},x_{2},n,space,base \right)}$$
$$Y{\left(y_{1},y_{2},n,space,base \right)} = \lambda{\left(y_{1},y_{2},n,space,base \right)}$$
$$Z{\left(z_{1},z_{2},n,space,base \right)} = \lambda{\left(z_{1},z_{2},n,space,base \right)}$$


```python
cartesian.X(n=5)
```

`array([0.  , 0.25, 0.5 , 0.75, 1.  ])`

```python
cartesian.X(n=5, space='log')
```

`array([ 1.        ,  1.77827941,  3.16227766,  5.62341325, 10.        ])`


By default, the space argument is a dictionary specifying optional values

```python
from kamodo import get_defaults
get_defaults(cartesian.X)
```

```
{'x_1': 0.0,
 'x_2': 1.0,
 'n': 100,
 'space': {'linear': 'linear', 'log': 'log'},
 'base': 10}
 ```


This allows function parsers to determine what values are valid for this entry and expose these options to the end user. For example, `space` above would be dropdown allowing the user to specify between `linear` and `log` options.


It is up to the function to raise a `NotImplementedError` for invalid inputs. 

```python
try:
    cartesian.X(space='dirt')
except NotImplementedError as m:
    print(m)
```

`unknown space: dirt`


## Plotting

```python
k = Kamodo(f='x**2-x-1')
```

Suppose we wish to evaluate `f` over a logarithmic space $x_i \in X$

```python
k.plot(f=dict(x=cartesian.X(n=10, space='log')))
```

This means the user can plot f in different spaces without registering a new function for `f` with alternate defaults each time.
