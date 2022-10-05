# 2022-10-05 16:48:31.261260: clock-out

* badge
* correct bug in action
* fail gracefully
* code coverage

# 2022-10-05 16:02:51.512151: clock-in

# 2022-10-05 14:55:08.872080: clock-out

* moving to another directory
* install kamodo
* changed to shell
* removing plane_type
* pytest

# 2022-10-05 13:51:00.401968: clock-in

* added phi modulus
* vector order usage
* allow setting order of vectors
* fixed shell and relative import
* documenting units

# 2022-02-18 16:55:27.831400: clock-out

* convert to classes, test 2d arrays

# 2022-02-18 16:16:57.686073: clock-in

# 2022-02-17 19:22:45.184678: clock-out

* added longitude wrap, Cartesian class

# 2022-02-17 18:53:52.698369: clock-in: T-30m 

* reshaping vector components

# 2022-02-16 18:52:00.097044: clock-out

* supporting vector conversion

# 2022-02-16 18:39:47.400053: clock-in

* adding vectors
* renaming for imports

# 2022-02-16 15:31:13.068086: clock-out

* added spherical, cartesian, geo coordinates

# 2022-02-16 13:55:42.766552: clock-in

# 2022-02-16 12:54:19.927791: clock-out

* Need to separate coordinate conversions into their own objects:
spherical - conversions from spherical into geo, cart:
* `x = r*sin(theta)*cos(phi)`
* `alt = r-6371*1000`
cartesian - conversions from cartesian to geo, sph 
geo - conversions from geo to sph, cart

This allows us to keep the registered names as simple as possible

# 2022-02-16 12:44:15.876830: clock-in

# 2022-02-11 18:34:50.206771: clock-out

* registering lambdas to avoid issue with order override

# 2022-02-11 18:31:46.600809: clock-in: T-10m 

# 2022-01-21 17:46:37.739782: clock-out

* examples

# 2022-01-21 17:20:06.089686: clock-in

# 2022-01-21 13:54:54.301885: clock-out

* added spherical slices

# 2022-01-21 12:01:08.418070: clock-in

# 2022-01-20 17:28:45.955482: clock-out

* added planar function

# 2022-01-20 16:15:34.852363: clock-in

# 2022-01-20 15:02:08.069639: clock-out

* adding planar cuts

# 2022-01-20 12:11:11.473419: clock-in

# 2022-01-19 19:26:45.698256: clock-out

* easier to read
* set up linear and log spaces, plotting example

# 2022-01-19 17:29:59.055946: clock-in

