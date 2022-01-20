# +
from kamodo import Kamodo, kamodofy
from kamodo import get_defaults, get_args
import numpy as np

def optional(d):
    """Get the first value if d is a dicitonary"""
    if isinstance(d, dict):
        return next(iter(d.values()))
    return d

def one_dimensional(x_1, x_2, n, space, base):
    if space == 'linear':
        return np.linspace(x_1, x_2, n)
    elif space == 'log':
        return np.logspace(x_1, x_2, n, base=base)
    else:
        raise NotImplementedError('unknown space: {}'.format(space))

def plot_dict(func, params):
    """map function arguments to input parameters
    example:
        >>> plot_dict(lambda x, y: x*y, (3,4))
        >>> {'x': 3, 'y': 4}
    """
    keys = get_args(func)
    if len(keys) == len(params):
        return {k: p for k, p in zip(keys, params)}
    else:
        raise NotImplementedError('cannot map {} to {} params'.format(keys, len(params)))


# -

# ## 1-dimensional spaces
#
# These functions may be used to generate Cartesian one-dimensional values.

# +
@kamodofy(data={})
def x(x_1=0., x_2=1., n=51, space=dict(linear='linear', log='log'), base=10):
    return one_dimensional(x_1, x_2, n, optional(space), base)

@kamodofy(data={})
def y(y_1=0., y_2=1., n=52, space=dict(linear='linear', log='log'), base=10):
    return one_dimensional(y_1, y_2, n, optional(space), base)

@kamodofy(data={})
def z(z_1=0., z_2=1., n=53, space=dict(linear='linear', log='log'), base=10):
    return one_dimensional(z_1, z_2, n, optional(space), base)


# -

# ## 2-dimensional spaces
#
# These may be used to generate cut planes along different axes.

# +
meshgrid_tooltip = """
Giving the string 'ij' returns a meshgrid with
matrix indexing, while 'xy' returns a meshgrid with Cartesian indexing.
In the 2-D case with inputs of length M and N, the outputs are of shape
(N, M) for 'xy' indexing and (M, N) for 'ij' indexing.
""".replace('\n', '<br>').strip('<br>')

@kamodofy(data={})
def xy(x_1=0., x_2=1., nx=51, xspace=dict(linear='linear', log='log'), xbase=10,
       y_1=0., y_2=1., ny=52, yspace=dict(linear='linear', log='log'), ybase=10,
       z={'None': None, '0': 0},
       squeeze={'True': True, 'False': False},
       indexing={'xy': 'xy', 'ij':'ij', 'tooltip': meshgrid_tooltip}):
    """create an xy-plane passing through z(optional)
    Todo: implement squeeze
    if squeeze: return xx_ij, yy_ij, z
    else: return xx_ijk, yy_ijk, zz_ijk
    """
    
    z_ = optional(z)
    squeeze = optional(squeeze)
    if z_ is not None:
        return np.meshgrid(
            one_dimensional(x_1, x_2, nx, optional(xspace), xbase),
            one_dimensional(y_1, y_2, ny, optional(yspace), ybase),
            z,
            indexing=optional(indexing))
    else:
        return np.meshgrid(
            one_dimensional(x_1, x_2, nx, optional(xspace), xbase),
            one_dimensional(y_1, y_2, ny, optional(yspace), ybase),
            indexing=optional(indexing))


@kamodofy(data={})
def xz(x_1=0., x_2=1., nx=51, xspace=dict(linear='linear', log='log'), xbase=10,
       y={'None': None, '0': 0},
       z_1=0., z_2=1., nz=53, zspace=dict(linear='linear', log='log'), zbase=10,
      indexing={'xz': 'xy', 'ij':'ij', 'tooltip': meshgrid_tooltip}):
    "create an xz plane passing through y (optional)"
    y_ = optional(y)
    if y_ is not None:
        return np.meshgrid(
            one_dimensional(x_1, x_2, nx, optional(xspace), xbase),
            y_,
            one_dimensional(z_1, z_2, nz, optional(zspace), zbase),
            indexing=optional(indexing))
    else:
        return np.meshgrid(one_dimensional(x_1, x_2, nx, optional(xspace), xbase),
                   one_dimensional(z_1, z_2, nz, optional(zspace), zbase),
                   indexing=optional(indexing))

@kamodofy(data={})
def yz(x={'None': None, '0': 0},
       y_1=0., y_2=1., ny=52, yspace=dict(linear='linear', log='log'), ybase=10,
       z_1=0., z_2=1., nz=53, zspace=dict(linear='linear', log='log'), zbase=10,
      indexing={'yz': 'xy', 'ij':'ij', 'tooltip': meshgrid_tooltip}):
    """create a yz plane passing through x (optional)"""
    x_ = optional(x)
    if x_ is not None:
        return np.meshgrid(
            x_,
            one_dimensional(y_1, y_2, ny, optional(yspace), ybase),
            one_dimensional(z_1, z_2, nz, optional(zspace), zbase),
            indexing=optional(indexing))
    else:
        return np.meshgrid(
            one_dimensional(y_1, y_2, ny, optional(yspace), ybase),
            one_dimensional(z_1, z_2, nz, optional(zspace), zbase),
            indexing=optional(indexing))

cartesian = Kamodo(X=x, Y=y, Z=z, XY=xy, XZ=xz, YZ=yz)
