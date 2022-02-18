from kamodo import Kamodo, kamodofy
import numpy as np


def to_tuple(vec):
    """convert numpy vector into tuple shape"""
    if hasattr(vec, 'shape'):
        return vec.T
    return vec


# # Spherical
#
# Conversions from spherical into geo, cartesian

# +
spherical = Kamodo()
@kamodofy(#arg_units=dict(r='1', theta='rad', phi='rad'),
         equation='r sin(\\theta) cos(\phi)')
def x_sph(r, theta, phi):
    return r*np.sin(theta)*np.cos(phi)

@kamodofy(equation='r sin(\\theta) sin(\phi)')
def y_sph(r, theta, phi):
    return r*np.sin(theta)*np.sin(phi)

@kamodofy(equation='r cos(\\theta)')
def z_sph(r, theta):
    return r*np.cos(theta)
    
spherical['x'] = x_sph
spherical['y'] = y_sph
spherical['z'] = z_sph

@kamodofy(units='deg', arg_units=dict(phi='rad'),
          equation='180 \\phi / \pi')
def lon_sph(phi):
    '''Geographic longitude'''
    return 180*phi/np.pi

@kamodofy(units='deg', arg_units=dict(theta='rad'),
          equation='90(1-2 \\theta /\pi)')
def lat_sph(theta):
    """Gegraphic latitude"""
    return 90*(1-2*theta/np.pi)


spherical['lon'] = lon_sph
spherical['lat'] = lat_sph
spherical['alt(r[m])[m]'] = 'r-6371*1000'
spherical['rvec'] = lambda r, theta, phi: np.array((r, theta, phi)).T

@kamodofy
def xvec_sph(rvec):
    """convert from (r,theta,phi) to (x,y,z)"""
    r, theta, phi = to_tuple(rvec)
    x = spherical.x(r, theta, phi)
    y = spherical.y(r,theta, phi)
    z = spherical.z(r, theta)
    return np.array([x, y, z]).T

spherical['xvec'] = xvec_sph

@kamodofy
def hvec_sph(rvec):
    """convert from (r[m], theta[rad], phi[rad]) to (lon[deg], lat[deg], alt[m])"""
    r, theta, phi = to_tuple(rvec)
    lat = spherical.lat(theta)
    lon = spherical.lon(phi)
    alt = spherical.alt(r)
    return np.array((lon, lat, alt)).T

spherical['hvec'] = hvec_sph


# +
def test_spherical():
    assert np.isclose(spherical.x(1, np.pi/2, 0), 1)
    assert np.isclose(spherical.y(1, np.pi/2, np.pi/2), 1)
    assert np.isclose(spherical.z(1, 0), 1)
    assert spherical.lon(np.pi/2) == 90
    assert spherical.lat(0) == 90
    assert spherical.alt(6371*1000) == 0
    assert np.isclose(spherical.xvec((1, np.pi/2, 0)), np.array([1, 0, 0])).all()
    assert np.isclose(spherical.hvec((6371*1000, np.pi/2, 0)), np.array([0, 0, 0])).all()

test_spherical()
# -

spherical


# ## Cartesian
#
# From cartesian to spherical, geo

# +
class Cartesian(Kamodo):
    def __init__(self, longitude_modulus = 360, **kwargs):
        
        self.longitude_modulus = longitude_modulus
        
        super(Cartesian, self).__init__(**kwargs)
        
        self.register_spherical()
        self.register_geographic()
        
        self['xvec'] = lambda x, y, z: np.array((x, y, z)).T
        
    def register_spherical(self):
        self['r'] = 'sqrt(x_**2 + y_**2 + z_**2)'
        self['theta'] = 'acos(z_/r)'
        self['phi'] = 'atan2(y_, x_)'
        
        @kamodofy
        def rvec_cart(xvec):
            """convert from x,y,z to r, theta, phi"""
            x, y, z = to_tuple(xvec)
            r = cartesian.r(x,y,z)
            theta = cartesian.theta(x,y,z)
            phi = cartesian.phi(x,y)
            return np.array((r, theta, phi)).T
        
        self['rvec'] = rvec_cart
    
    def register_geographic(self):
        lon_equation = 'mod(180 atan2(y, x)/\pi, {})'.format(self.longitude_modulus)
        @kamodofy(units='deg', equation=lon_equation)
        def lon_cart(x, y):
            phi = np.arctan2(y,x)
            return (180*phi/np.pi)%self.longitude_modulus

        self['lon'] = lon_cart
        
        @kamodofy(units='deg', arg_units=dict(theta='rad'),
          equation='90(1-2 acos(z/\sqrt{x^2+y^2+z^2}) /\pi)')
        def lat_cart(x, y, z):
            """Gegraphic latitude"""
            r = np.sqrt(x**2+y**2+z**2)
            return 90*(1-2*(np.arccos(z/r))/np.pi)

        self['lat'] = lat_cart

        @kamodofy(units='m', arg_units=dict(x='m', y='m', z='m'),
                 equation='\sqrt{x^2+y^2+z^2} - 6371000')
        def alt_cart(x, y, z):
            r = np.sqrt(x**2+y**2+z**2)
            return r - 6371*1000

        self['alt'] = alt_cart
        
        @kamodofy(arg_units=dict(xvec='m'))
        def hvec_cart(xvec):
            """convert from (x,y,z) to (lon, lat, alt)"""
            x, y, z = to_tuple(xvec)
            alt = cartesian.alt(x,y,z)
            lat = cartesian.lat(x,y,z)
            lon = cartesian.lon(x,y)
            return np.array((lon, lat, alt)).T

        self['hvec'] = hvec_cart
        

cartesian = Cartesian()


# +
def test_cartesian():
    assert cartesian.alt(6371*1000, 0, 0) == 0
    assert cartesian.lat(0, 0, 6371*1000) == 90
    assert cartesian.lon(0, 6371*1000) == 90
    assert cartesian.r(1, 0, 0) == 1
    assert np.isclose(cartesian.theta(1, 0, 0), np.pi/2)
    assert np.isclose(cartesian.phi(0, 1), np.pi/2)
    assert np.isclose(cartesian.rvec((1, 0, 0)), np.array([1, np.pi/2, 0])).all()
    assert np.isclose(cartesian.hvec((6371*1000, 0, 0)), np.array([0, 0, 0])).all()
    
test_cartesian()

cartesian
# -

# ## Geographic
# Convert from geographic (lon, lat, alt) to Cartesian, spherical

# +
geographic = Kamodo()

geographic['r(alt[m])[m]'] = 'alt+6371*1000'

@kamodofy(units='rad', arg_units=dict(lat='deg'),
         equation='(1-(lat/90))\pi/2')
def theta_geo(lat):
    return (1-(lat/90))*np.pi/2

geographic['theta'] = theta_geo

@kamodofy(units='rad', arg_units=dict(lon='deg'),
         equation='\pi lon/180')
def phi_geo(lon):
    return lon*np.pi/180

geographic['phi'] = phi_geo

geographic['x'] = 'r*sin(theta)*cos(phi)'
geographic['y'] = 'r*sin(theta)*sin(phi)'
geographic['z'] = 'r*cos(theta)'
geographic['hvec'] = lambda lon, lat, alt: np.array((lon, lat, alt)).T

@kamodofy
def xvec_geo(hvec):
    """convert from (lon[deg], lat[deg], alt[m]) to (x, y, z)"""
    lon, lat, alt = to_tuple(hvec)
    x = geographic.x(alt, lat, lon)
    y = geographic.y(alt, lat, lon)
    z = geographic.z(alt, lat)
    return np.array((x,y,z)).T

geographic['xvec'] = xvec_geo

@kamodofy
def rvec_geo(hvec):
    """convert from (lon[deg], lat[deg], alt[m]) to (r, theta, phi)"""
    lon, lat, alt = to_tuple(hvec)
    r = geographic.r(alt)
    theta = geographic.theta(lat)
    phi = geographic.phi(lon)
    return np.array((r, theta, phi)).T

geographic['rvec'] = rvec_geo


# +
def test_geographic():
    assert geographic.x(0, 0, 0) == 6371*1000
    assert geographic.y(0, 0, 90) == 6371*1000
    assert geographic.z(0, 90) == 6371*1000
    assert np.isclose(geographic.xvec((0, 0, 0)), np.array([6371*1000, 0, 0])).all()
    assert np.isclose(geographic.rvec((0, 0, 0)), np.array([6371*1000, np.pi/2, 0])).all()

test_geographic()
geographic
