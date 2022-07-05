from kamodo import Kamodo, kamodofy
import numpy as np


def to_tuple(vec):
    """convert numpy vector into tuple shape"""
    if hasattr(vec, 'shape'):
        return np.moveaxis(vec, -1, 0)
    return vec


# # Spherical
#
# Conversions from spherical into geo, cartesian

class Spherical(Kamodo):
    def __init__(self, **kwargs):
        super(Spherical, self).__init__(**kwargs)
        
        self.register_cartesian()
        
        self.register_geographic()
        
        self['rvec'] = lambda r, theta, phi: np.stack((r, theta, phi), axis=-1)
        
    def register_cartesian(self):
        """register conversions from spherical to cartesian"""
        
        @kamodofy(#arg_units=dict(r='1', theta='rad', phi='rad'),
                 equation='r sin(\\theta) cos(\phi)')
        def x_sph(r, theta, phi):
            return r*np.sin(theta)*np.cos(phi)
        
        self['x'] = x_sph
        
        @kamodofy(equation='r sin(\\theta) sin(\phi)')
        def y_sph(r, theta, phi):
            return r*np.sin(theta)*np.sin(phi)
        
        self['y'] = y_sph
        
        @kamodofy(equation='r cos(\\theta)')
        def z_sph(r, theta):
            return r*np.cos(theta)
        
        self['z'] = z_sph
        
        @kamodofy
        def xvec_sph(rvec):
            """convert from (r,theta,phi) to (x,y,z)"""
            r, theta, phi = to_tuple(rvec)
            x = self.x(r, theta, phi)
            y = self.y(r,theta, phi)
            z = self.z(r, theta)
            return np.stack((x, y, z), axis=-1)
        
        self['xvec'] = xvec_sph
    
    def register_geographic(self):
        """register conversions from spherical to geographic"""
    
        @kamodofy(units='deg', arg_units=dict(phi='rad'),
                  equation='180 \\phi / \pi')
        def lon_sph(phi):
            '''Geographic longitude'''
            return 180*phi/np.pi
        
        self['lon'] = lon_sph
        
        @kamodofy(units='deg', arg_units=dict(theta='rad'),
                  equation='90(1-2 \\theta /\pi)')
        def lat_sph(theta):
            """Gegraphic latitude"""
            return 90*(1-2*theta/np.pi)

        self['lat'] = lat_sph
        
        self['alt(r[m])[m]'] = 'r-6371*1000'
        
        @kamodofy
        def hvec_sph(rvec):
            """convert from (r[m], theta[rad], phi[rad]) to (lon[deg], lat[deg], alt[m])"""
            r, theta, phi = to_tuple(rvec)
            lat = self.lat(theta)
            lon = self.lon(phi)
            alt = self.alt(r)
            return np.stack((lon, lat, alt), axis=-1)
        
        self['hvec'] = hvec_sph


# need to test vectorization

spherical = Spherical()
spherical


# +
def test_spherical():
    spherical = Spherical()
    assert np.isclose(spherical.x(1, np.pi/2, 0), 1)
    assert np.isclose(spherical.y(1, np.pi/2, np.pi/2), 1)
    assert np.isclose(spherical.z(1, 0), 1)
    assert spherical.lon(np.pi/2) == 90
    assert spherical.lat(0) == 90
    assert spherical.alt(6371*1000) == 0
    assert np.isclose(spherical.xvec((1, np.pi/2, 0)), np.array([1, 0, 0])).all()
    assert np.isclose(spherical.hvec((6371*1000, np.pi/2, 0)), np.array([0, 0, 0])).all()

    r = np.linspace(0, 1, 20).reshape((4,5))
    theta = np.linspace(0, np.pi, 20).reshape((4,5))
    phi = np.linspace(-np.pi, np.pi, 20).reshape((4,5))

    rvec = spherical.rvec(r, theta, phi)
    for i, _ in enumerate((r, theta, phi)):
        assert (_== rvec[:,:,i]).all()

test_spherical()


# -

# ## Cartesian
#
# From cartesian to spherical, geo

class Cartesian(Kamodo):
    def __init__(self,
        longitude_modulus = 360,
        phi_modulus = None,
        rvec_order = ['r', 'theta', 'phi'],
        hvec_order = ['lon', 'lat', 'alt'],
        **kwargs):
        
        self.longitude_modulus = longitude_modulus
        self.phi_modulus = phi_modulus
        self._rvec_order = rvec_order
        self._hvec_order = hvec_order

        super(Cartesian, self).__init__(**kwargs)
        
        self.register_spherical()
        self.register_geographic()
        
        self['xvec'] = lambda x, y, z: np.stack((x, y, z), axis=-1)
        
    def register_spherical(self):
        self['r'] = 'sqrt(x_**2 + y_**2 + z_**2)'
        self['theta'] = 'acos(z_/r)'
        if self.phi_modulus is None:
            self['phi'] = 'atan2(y_, x_)'
        else:
            self['phi'] = 'mod(atan2(y_, x_),{})'.format(self.phi_modulus)
        
        @kamodofy
        def rvec_cart(xvec):
            """convert from x,y,z to r, theta, phi"""
            x, y, z = to_tuple(xvec)
            r = self.r(x,y,z)
            theta = self.theta(x,y,z)
            phi = self.phi(x,y)
            coord_dict = dict(r=r, theta=theta, phi=phi)
            rvec = [coord_dict[_] for _ in self._rvec_order]
            return np.stack(rvec, axis=-1)
        
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
            """convert from [x[m],y[m],z[m]] to [lon[deg], lat[deg], alt[m]]"""
            x, y, z = to_tuple(xvec)
            alt = self.alt(x,y,z)
            lat = self.lat(x,y,z)
            lon = self.lon(x,y)
            coord_dict = dict(lon=lon, lat=lat, alt=alt)
            hvec = [coord_dict[_] for _ in self._hvec_order]
            return np.stack(hvec, axis=-1)

        self['hvec'] = hvec_cart


# +
def test_cartesian():
    cartesian = Cartesian()
    assert cartesian.alt(6371*1000, 0, 0) == 0
    assert cartesian.lat(0, 0, 6371*1000) == 90
    assert cartesian.lon(0, 6371*1000) == 90
    assert cartesian.r(1, 0, 0) == 1
    assert np.isclose(cartesian.theta(1, 0, 0), np.pi/2)
    assert np.isclose(cartesian.phi(0, 1), np.pi/2)
    assert np.isclose(cartesian.rvec((1, 0, 0)), np.array([1, np.pi/2, 0])).all()
    assert np.isclose(cartesian.hvec((6371*1000, 0, 0)), np.array([0, 0, 0])).all()

    x = np.linspace(-1, 1, 20).reshape((4,5))
    y = np.linspace(-1, 1, 20).reshape((4,5))
    z = np.linspace(-1, 1, 20).reshape((4,5))

    xvec = cartesian.xvec(x, y, z)
    for i, _ in enumerate((x, y, z)):
        assert (_== xvec[:,:,i]).all()
    
test_cartesian()
# -

# ## Geographic
# Convert from geographic (lon, lat, alt) to Cartesian, spherical

class Geographic(Kamodo):
    def __init__(self, **kwargs):
        
        super(Geographic, self).__init__(**kwargs)

        self.register_spherical()
        self.register_cartesian()
        self['hvec'] = lambda lon, lat, alt: np.stack((lon, lat, alt), axis=-1)

    def register_spherical(self):
        """convert from geographic to spherical"""

        self['r(alt[m])[m]'] = 'alt+6371*1000'

        @kamodofy(units='rad', arg_units=dict(lat='deg'),
                 equation='(1-(lat/90))\pi/2')
        def theta_geo(lat):
            return (1-(lat/90))*np.pi/2

        self['theta'] = theta_geo

        @kamodofy(units='rad', arg_units=dict(lon='deg'),
                 equation='\pi lon/180')
        def phi_geo(lon):
            return lon*np.pi/180

        self['phi'] = phi_geo

        @kamodofy
        def rvec_geo(hvec):
            """convert from (lon[deg], lat[deg], alt[m]) to (r, theta, phi)"""
            lon, lat, alt = to_tuple(hvec)
            r = self.r(alt)
            theta = self.theta(lat)
            phi = self.phi(lon)
            return np.stack((r, theta, phi), axis=-1)

        self['rvec'] = rvec_geo

    def register_cartesian(self):
        """convert from geographic to cartesian

        r, theta, phi already registered by now so use kamodo's autoreplacement
        """

        self['x'] = 'r*sin(theta)*cos(phi)'
        self['y'] = 'r*sin(theta)*sin(phi)'
        self['z'] = 'r*cos(theta)'


        @kamodofy
        def xvec_geo(hvec):
            """convert from (lon[deg], lat[deg], alt[m]) to (x, y, z)"""
            lon, lat, alt = to_tuple(hvec)
            x = self.x(alt, lat, lon)
            y = self.y(alt, lat, lon)
            z = self.z(alt, lat)
            return np.stack((x,y,z), axis=-1)

        self['xvec'] = xvec_geo

# +
def test_geographic():
    geographic = Geographic()
    assert geographic.x(0, 0, 0) == 6371*1000
    assert geographic.y(0, 0, 90) == 6371*1000
    assert geographic.z(0, 90) == 6371*1000
    assert np.isclose(geographic.xvec((0, 0, 0)), np.array([6371*1000, 0, 0])).all()
    assert np.isclose(geographic.rvec((0, 0, 0)), np.array([6371*1000, np.pi/2, 0])).all()

    lon = np.linspace(-180, 180, 20).reshape((4,5))
    lat = np.linspace(-90, 90, 20).reshape((4,5))
    alt = np.linspace(0, 100, 20).reshape((4,5))

    hvec = geographic.hvec(lon, lat, alt)
    for i, _ in enumerate((lon, lat, alt)):
        assert (_== hvec[:,:,i]).all()

test_geographic()
# -


