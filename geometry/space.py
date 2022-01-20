from kamodo import Kamodo, kamodofy
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

@kamodofy
def x(x_1=0., x_2=1., n=100, space=dict(linear='linear', log='log'), base=10):
    return one_dimensional(x_1, x_2, n, optional(space), base)

@kamodofy
def y(y_1=0., y_2=1., n=100, space=dict(linear='linear', log='log'), base=10):
    return one_dimensional(y_1, y_2, n, optional(space), base)

@kamodofy
def z(z_1=0., z_2=1., n=100, space=dict(linear='linear', log='log'), base=10):
    return one_dimensional(z_1, z_2, n, optional(space), base)


cartesian = Kamodo(X=x, Y=y, Z=z)
