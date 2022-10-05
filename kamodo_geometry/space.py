# +
from kamodo import Kamodo, kamodofy
from kamodo import get_defaults, get_args
import numpy as np

def optional(d):
    """Get the first value if d is a dicitonary"""
    if isinstance(d, dict):
        return next(iter(d.values()))
    return d

def optionals(*args):
    return [optional(_) for _ in args]

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
        if squeeze:
            x_, y_ = np.meshgrid(
                one_dimensional(x_1, x_2, nx, optional(xspace), xbase),
                one_dimensional(y_1, y_2, ny, optional(yspace), ybase),
                indexing=optional(indexing))
            return x_, y_, z_
        return np.meshgrid(
            one_dimensional(x_1, x_2, nx, optional(xspace), xbase),
            one_dimensional(y_1, y_2, ny, optional(yspace), ybase),
            z,
            indexing=optional(indexing))
    return np.meshgrid(
        one_dimensional(x_1, x_2, nx, optional(xspace), xbase),
        one_dimensional(y_1, y_2, ny, optional(yspace), ybase),
        indexing=optional(indexing))


@kamodofy(data={})
def xz(x_1=0., x_2=1., nx=51, xspace=dict(linear='linear', log='log'), xbase=10,
       y={'None': None, '0': 0},
       z_1=0., z_2=1., nz=53, zspace=dict(linear='linear', log='log'), zbase=10,
       squeeze={'True': True, 'False': False},
       indexing={'xz': 'xy', 'ij':'ij', 'tooltip': meshgrid_tooltip}):
    "create an xz plane passing through y (optional)"
    y_ = optional(y)
    squeeze = optional(squeeze)
    if y_ is not None:
        if squeeze:
            x_, z_ = np.meshgrid(
                one_dimensional(x_1, x_2, nx, optional(xspace), xbase),
                one_dimensional(z_1, z_2, nz, optional(zspace), zbase),
                indexing=optional(indexing))
            return x_, y_, z_
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
       squeeze={'True': True, 'False': False},
      indexing={'yz': 'xy', 'ij':'ij', 'tooltip': meshgrid_tooltip}):
    """create a yz plane passing through x (optional)"""
    x_ = optional(x)
    squeeze = optional(squeeze)
    if x_ is not None:
        if squeeze:
            y_, z_ = np.meshgrid(
                one_dimensional(y_1, y_2, ny, optional(yspace), ybase),
                one_dimensional(z_1, z_2, nz, optional(zspace), zbase),
                indexing=optional(indexing))
            return x_, y_, z_
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


# -

# ### Cartesian plane
#
# A more generic form of cartesian plane would be to specify all of the above with defaults

# +
@kamodofy
def planar(
        plane=dict(xy='xy', xz='xz', yz='yz'),
        x_1=0., x_2=1., nx=51, x=0,
        xspace=dict(linear='linear', log='log'), xbase=10,
        y_1=0., y_2=1., ny=52, y=0,
        yspace=dict(linear='linear', log='log'), ybase=10,
        z_1=0., z_2=1., nz=53, z=0,
        zspace=dict(linear='linear', log='log'), zbase=10,
        squeeze={'True': True, 'False': False},
        indexing={'yz': 'xy', 'ij':'ij', 'tooltip': meshgrid_tooltip}):
    """generic 3d cut plane"""
    plane = optional(plane)
    squeeze=optional(squeeze)
    indexing = optional(indexing)
    xspace, yspace, zspace = optionals(xspace, yspace, zspace)
    x_ = one_dimensional(x_1, x_2, nx, xspace, xbase)
    y_ = one_dimensional(y_1, y_2, ny, yspace, ybase)
    z_ = one_dimensional(z_1, z_2, nz, zspace, zbase)
    if plane == 'xy':
        if squeeze:
            xx, yy = np.meshgrid(x_, y_, indexing=indexing)
            return xx, yy, z
        return np.meshgrid(x_, y_, z, indexing=indexing)
    elif plane == 'xz':
        if squeeze:
            xx, zz = np.meshgrid(x_, z_, indexing=indexing)
            return xx, y, zz
        return np.meshgrid(x_, y, z_, indexing=indexing)
    elif plane == 'yz':
        if squeeze:
            yy, zz = np.meshgrid(y_, z_, indexing=indexing)
            return x, yy, zz
        return np.meshgrid(x, y_, z_, indexing=indexing)
    else:
        raise NotImplementedError('plane {} not supported'.format(plane))

cartesian['planar'] = planar


# -

@kamodofy(hidden_args = ['r_min', 'r_max', 'rspace', 'rbase', 'nr',
                         'theta_min', 'theta_max', 'ntheta',
                         'phi_min', 'phi_max', 'nphi',
                         'squeeze', 'indexing','shell',
                        ])
def shell(
        shell={'theta-phi':'theta-phi', 'r-theta':'r-theta', 'r-phi':'r-phi'},
        r_min=0., r_max=2., nr=51, r=1.0,
        rspace=dict(linear='linear', log='log'),
        rbase={'10': 10, '2': 2, 'e': np.e},
        theta_min=0., theta_max=np.pi, ntheta=52, theta=0,
        phi_min=0., phi_max=2*np.pi, nphi=53, phi=0,
        squeeze={'True': True, 'False': False},
        indexing={'rtheta': 'xy', 'ij':'ij', 'tooltip': meshgrid_tooltip}):
    shell = optional(shell)
    squeeze=optional(squeeze)
    indexing = optional(indexing)
    rbase = optional(rbase)
    rspace = optional(rspace)
    r_ = one_dimensional(r_min, r_max, nr, rspace, rbase)
    theta_ = one_dimensional(theta_min, theta_max, ntheta, 'linear', 1)
    phi_ = one_dimensional(phi_min, phi_max, nphi, 'linear', 1)
    if shell == 'r-theta':
        if squeeze:
            pphi = phi
            rr, ttheta = np.meshgrid(r_, theta_, indexing=indexing)
        else:
            rr, ttheta, pphi = np.meshgrid(r_, theta_, phi, indexing=indexing)
    elif shell == 'r-phi':
        if squeeze:
            ttheta = theta
            rr, pphi = np.meshgrid(r_, phi_, indexing=indexing)
        else:
            rr, ttheta, pphi = np.meshgrid(r_, theta, phi_, indexing=indexing)
    elif shell == 'theta-phi':
        if squeeze:
            rr = r
            ttheta, pphi = np.meshgrid(theta_, phi_, indexing=indexing)
        else:
            rr, ttheta, pphi = np.meshgrid(r, theta_, phi_, indexing=indexing)
    else:
        raise NotImplementedError('plane {} not supported'.format(shell))
    x = rr*np.sin(ttheta)*np.cos(pphi)
    y = rr*np.sin(pphi)*np.sin(ttheta)
    z = rr*np.cos(ttheta)
    return x, y, z



def shell_geo(
        shell={'lat-lon':'lat-lon', 'h-lat':'h-lat', 'h-lon':'h-lon'},      
        h_min=0., h_max=2., nh=51, h=1.0,                                   #dont know if defaults are right
        hspace=dict(linear='linear', log='log'),                            
        hbase={'10': 10, '2': 2, 'e': np.e},                                
        lat_min=-90., lat_max=90., nlat=52, lat=0,                          #dont know if defaults are right
        lon_min=0., lon_max=360., nlon=53, lon=0,                        #dont know if defaults are right
        squeeze={'True': True, 'False': False},
        indexing={'hlat': 'xy', 'ij':'ij', 'tooltip': meshgrid_tooltip}):
    shell = optional(shell)
    squeeze=optional(squeeze)
    indexing = optional(indexing)
    hbase = optional(hbase)
    hspace = optional(hspace)
    h_ = one_dimensional(h_min, h_max, nh, hspace, hbase)
    lat_ = one_dimensional(lat_min, lat_max, nlat, 'linear', 1)
    lon_ = one_dimensional(lon_min, lon_max, nlon, 'linear', 1)
    if shell == 'h-lat':
        if squeeze:
            llon = lon
            hh, llat = np.meshgrid(h_, lat_, indexing=indexing)
        else:
            hh, llat, llon = np.meshgrid(h_, lat_, lon, indexing=indexing)
    elif shell == 'h-lon':
        if squeeze:
            llat = lat
            hh, llon = np.meshgrid(h_, lon_, indexing=indexing)
        else:
            hh, llat, llon = np.meshgrid(h_, lat, lon_, indexing=indexing)
    elif shell == 'lat-lon':
        if squeeze:
            hh = h
            llat, llon = np.meshgrid(lat_, lon_, indexing=indexing)
        else:
            hh, llat, llot = np.meshgrid(h, lat_, lon_, indexing=indexing)
    else:
        raise NotImplementedError('plane {} not supported'.format(shell))
    rr = hh + 6371*1000
    ttheta = (1-(llat/90))*np.pi/2
    pphi = llon*np.pi/180
    x = rr*np.sin(ttheta)*np.cos(pphi) 
    y = rr*np.sin(pphi)*np.sin(ttheta) 
    z = rr*np.cos(ttheta) 
    return x, y, z



