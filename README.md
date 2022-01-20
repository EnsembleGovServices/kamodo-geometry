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

### 1d functions

```python
k = Kamodo(f='x**2-x-1')
```

Suppose we wish to evaluate `f` over a logarithmic space $x_i \in X$

```python
k.plot(f=dict(x=cartesian.X(n=10, space='log')))
```

This means the user can plot f in different spaces without registering a new function for `f` with alternate defaults each time.

```python
k.plot(f=dict(x=cartesian.X(x_1=-1, x_2 = 2, n=100, space='linear')))
```

## 2-d Functions


For 2-d functions, we need geometries that create surfaces. The simplest of these are the `X-Y`, `X-Z` and `Y-Z` planar cartesian cuts.

```python
xx, yy = cartesian.XY()
print(xx.shape, yy.shape)
```

The parameters are similar to the 1-d functions above, except for the `indexing` parameter, which includes a tooltip to be shown to the end user:

```python
get_defaults(cartesian.XY)
```

The `plot_dict` function may be used to map function arguments to parameters. This is useful for getting the keyword arguments necessary to connect a function's parameters to the output of a gridding function (so we can pass the result to `k.plot`).

```python
from geometry.space import plot_dict

plot_dict(lambda alpha_, beta_: a*b, cartesian.XY())
```

```python
k = Kamodo(rho='alpha_**2 + beta_**2')
k.plot(rho=plot_dict(k.rho, cartesian.XY(yspace='log', xspace='log')))
```

## 3-dimensional cuts

For 3-D cut-planes, assume the function can handle planar inputs where two of the variables have the same shape:


```python
k = Kamodo(rho='sin(5*x)*cos(7*y)*z')
k
```

```python
k.plot(rho=plot_dict(k.rho, cartesian.XY(z=2)))
```

```python
k.plot(rho=plot_dict(k.rho, cartesian.YZ(x=1)))
```

We can also use the more generic `planar` function.

```python
k.plot(rho=plot_dict(k.rho, cartesian.planar('yz', x=1, ny=111, yspace='log')))
```

## Gridify

When we are given a function of vector-valued positions (provided by some external resource), we can convert such functions into "gridified" form for plotting.

```python
from kamodo import kamodofy
@kamodofy
def rho(rvec):
    # r*cos(2y)*sin(5x) for (x,y) = rvec and r = |rvec|
    return np.cos(2*rvec[:,1])*np.sin(5*rvec[:,0])*np.linalg.norm(rvec, axis=1)

k['rho'] = rho

k.rho 
```

```python
# rho takes Nx3 positions as input and returns shape (N,) as output
k.rho(cartesian.X(n=7*3).reshape(7,3)).shape
```

Register a new function that converts rho(rvec) to rho(x,y,z) using the `gridify` decorator.

```python
from kamodo import gridify

k['rho_grid'] = gridify(k.rho, # function to be converted
                        x=cartesian.X(), # parameterization to use
                        y=cartesian.Y(space='log'), # can mix with log
                        z=0, # intercept
                        squeeze=False, # keep the 3rd dimension of the output
                       )
k.plot('rho_grid')
```

```python

```

```python

```
