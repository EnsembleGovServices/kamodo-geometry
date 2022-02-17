from kamodo import Kamodo, kamodofy
import numpy as np

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
spherical['alt(r[km])[km]'] = 'r-6371'
spherical['rvec'] = lambda r, theta, phi: np.vstack((np.array(r),np.array(theta),np.array(phi))).T

@kamodofy
def xvec_sph(rvec):
    """convert from (r,theta,phi) to (x,y,z)"""
    r, theta, phi = np.array(rvec).T
    x = spherical.x(r, theta, phi)
    y = spherical.y(r,theta, phi)
    z = spherical.z(r, theta)
    return np.vstack((x,y,z)).T

spherical['xvec'] = xvec_sph

@kamodofy
def hvec_sph(rvec):
    """convert from (r[km], theta[rad], phi[rad]) to (lat[deg], lon[deg], alt[km])"""
    r, theta, phi = np.array(rvec).T
    lat = spherical.lat(theta)
    lon = spherical.lon(phi)
    alt = spherical.alt(r)
    return np.vstack((lat, lon, alt)).T

spherical['hvec'] = hvec_sph


# -

def test_spherical():
    assert np.isclose(spherical.x(1, np.pi/2, 0), 1)
    assert np.isclose(spherical.y(1, np.pi/2, np.pi/2), 1)
    assert np.isclose(spherical.z(1, 0), 1)
    assert spherical.lon(np.pi/2) == 90
    assert spherical.lat(0) == 90
    assert spherical.alt(6371) == 0
    assert np.isclose(spherical.xvec((1, np.pi/2, 0)), np.array([1, 0, 0])).all()
    assert np.isclose(spherical.hvec((6371, np.pi/2, 0)), np.array([0, 0, 0])).all()
test_spherical()

spherical

# ## Cartesian
#
# From cartesian to spherical, geo

# +
cartesian = Kamodo()

cartesian['r'] = 'sqrt(x_**2 + y_**2 + z_**2)'
cartesian['theta'] = 'acos(z_/r)'
cartesian['phi'] = 'atan2(y_, x_)'

@kamodofy(units='deg', equation='180 atan2(y, x)/\pi')
def lon_cart(x, y):
    phi = np.arctan2(y,x)
    return 180*phi/np.pi

cartesian['lon'] = lon_cart

@kamodofy(units='deg', arg_units=dict(theta='rad'),
          equation='90(1-2 acos(z/\sqrt{x^2+y^2+z^2}) /\pi)')
def lat_cart(x, y, z):
    """Gegraphic latitude"""
    r = np.sqrt(x**2+y**2+z**2)
    return 90*(1-2*(np.arccos(z/r))/np.pi)

cartesian['lat'] = lat_cart

@kamodofy(units='km', arg_units=dict(x='km', y='km', z='km'),
         equation='\sqrt{x^2+y^2+z^2} - 6371')
def alt_cart(x, y, z):
    r = np.sqrt(x**2+y**2+z**2)
    return r - 6371

cartesian['alt'] = alt_cart
cartesian['xvec'] = lambda x, y, z: np.vstack((np.array(x),np.array(y),np.array(z))).T

@kamodofy
def rvec_cart(xvec):
    """convert from x,y,z to r, theta, phi"""
    x, y, z = np.array(xvec).T
    r = cartesian.r(x,y,z)
    theta = cartesian.theta(x,y,z)
    phi = cartesian.phi(x,y)
    return np.vstack((r,theta,phi)).T
    
cartesian['rvec'] = rvec_cart


@kamodofy(arg_units=dict(xvec='km'))
def hvec_cart(xvec):
    """convert from (x,y,z) to (lat, lon, alt)"""
    x, y, z = np.array(xvec).T
    alt = cartesian.alt(x,y,z)
    lat = cartesian.lat(x,y,z)
    lon = cartesian.lon(x,y)
    return np.vstack((lon,lat,alt)).T

cartesian['hvec'] = hvec_cart


# +
def test_cartesian():
    assert cartesian.alt(6371, 0, 0) == 0
    assert cartesian.lat(0, 0, 6371) == 90
    assert cartesian.lon(0, 6371) == 90
    assert cartesian.r(1, 0, 0) == 1
    assert np.isclose(cartesian.theta(1, 0, 0), np.pi/2)
    assert np.isclose(cartesian.phi(0, 1), np.pi/2)
    assert np.isclose(cartesian.rvec((1, 0, 0)), np.array([1, np.pi/2, 0])).all()
    assert np.isclose(cartesian.hvec((6371, 0, 0)), np.array([0, 0, 0])).all()
    
test_cartesian()

cartesian
# -

# ## Geographic
# Convert from geographic (lon, lat, alt) to Cartesian, spherical

# +
geographic = Kamodo()

geographic['r(alt[km])[km]'] = 'alt+6371'

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
geographic['hvec'] = lambda lon, lat, alt: np.vstack((np.array(lon),np.array(lat),np.array(alt))).T

@kamodofy
def xvec_geo(hvec):
    """convert from (lon[deg], lat[deg], alt[km]) to (x, y, z)"""
    lon, lat, alt = np.array(hvec).T
    x = geographic.x(alt, lat, lon)
    y = geographic.y(alt, lat, lon)
    z = geographic.z(alt, lat)
    return np.vstack((x,y,z)).T

geographic['xvec'] = xvec_geo

@kamodofy
def rvec_geo(hvec):
    """convert from (lon[deg], lat[deg], alt[km]) to (r, theta, phi)"""
    lon, lat, alt = np.array(hvec).T
    r = geographic.r(alt)
    theta = geographic.theta(lat)
    phi = geographic.phi(lon)
    return np.vstack((r, theta, phi)).T

geographic['rvec'] = rvec_geo


# +
def test_geographic():
    assert geographic.x(0, 0, 0) == 6371
    assert geographic.y(0, 0, 90) == 6371
    assert geographic.z(0, 90) == 6371
    assert np.isclose(geographic.xvec((0, 0, 0)), np.array([6371, 0, 0])).all()
    assert np.isclose(geographic.rvec((0, 0, 0)), np.array([6371, np.pi/2, 0])).all()

test_geographic()
geographic
