<!-- #region -->

# Kamodo Geometry

[![codecov](https://codecov.io/gh/EnsembleGovServices/kamodo-geometry/branch/master/graph/badge.svg)](https://codecov.io/gh/EnsembleGovServices/kamodo-geometry)

Geometric functions for advanced function composition.

## Motivation
Kamodo keeps a mapping between function signatures and specific plot types.
However, function authors may not be aware of the full context that their functions may be called, and this limits the kinds of plots available to end users.

This library contains a number of geometric functions that allow for much more flexibility in defining where functions should be evaluated. Each function contains many options not known to kamodo's plotting signatures, but which may be provisioned at run time.

## Install

Clone this repo and pip install in editable mode

```sh
git clone https://github.com/EnsembleGovServices/kamodo-geometry.git
pip install -e kamodo-geometry
```

You should now be able to import the `kamodo_geometry` module

```python
import kamodo_geometry
```

## Examples

```python
from kamodo import Kamodo
import numpy as np
```

```python
from kamodo_geometry.space import cartesian
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
from kamodo_geometry.space import plot_dict

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

## Parametric surfaces

A more general form of a surface is defined by `u-v` parameterization, where each of the `x,y,z` coordinates is itself a function of two variables `u,v`. This is useful for defining a spherical surface.

```python
k = Kamodo(x_ij=lambda u, v: np.sin(np.pi*v),
           y_ij=lambda u, v: np.cos(np.pi*u),
           z_ij=lambda u, v: u*v)

k['vec_3'] = lambda x,y,z: (x,y,z)
k['surface'] = 'vec_3(x_ij,y_ij,z_ij)'
k['rho'] = 'sin(3*x)*cos(5*y)*sin(7*z)'
k
```

```python
u, v = np.meshgrid(np.linspace(0,1,111),
                   np.linspace(0,1,113))
k.plot(rho=plot_dict(k.rho, k.surface(u,v)))
```

### Spherical Shell


Various slices may be made using `cartesian.shell` which represents spherical cross sections.

```python
from kamodo_geometry.space import shell
```

```python
help(shell)
```

By default, the cartesian shell is at fixed `r=1`

```python
k.plot(rho=plot_dict(k.rho, shell()))
```

```python
k.plot(rho=plot_dict(k.rho, shell(
    'r-theta',
    rspace='linear',
    theta_min=np.pi/8,
    theta_max=7*np.pi/8)))
```

```python
k.plot(rho=plot_dict(k.rho, shell('r-phi', r_max = 2, theta=2*np.pi/3)))
```

```python
from kamodo_geometry.coordinates import Cartesian
```

```python
Cartesian?
```

```python
cart = Cartesian(rvec_order=['r', 'theta', 'phi'])

assert cart.rvec([1, 0, 0])[0] == 1
```

```python
cart = Cartesian(rvec_order=['phi', 'theta', 'r'])

assert cart.rvec([1, 0, 0])[2] == 1
```
