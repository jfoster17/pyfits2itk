pyfits2itk
===========

pyfits2itk is a Python replacement for [fits2itk][1] from the IIC/Astronomical 
Medicine Project, which is no longer maintained. This module uses [astropy][2] 
to read in a FITS cube or image, performs some simple manipulations useful 
for converting astronomy data (such as flipping the RA/longitude axis) and
then calls the [pynrrd][3] module (included) to write out a [nrrd][4] file for 
inport into 3D programs such as Slicer3D.

Since Slicer3D does not understand astronomy coordinates, you must preregister
and congrid all cubes externally before converting them to nrrd.

There is limited support for converting astronomy coordinates into units
Slicer3D does understand. See Advanced Usage.

[1]: http://astromed.iic.harvard.edu/FITS-reader
[2]: http://www.astropy.org/
[3]: https://github.com/mhe/pynrrd
[4]: http://teem.sourceforge.net/nrrd/

Dependencies
------------

[astropy][1]

If you have astropy (which requires [numpy][2]) then you're 
good to go.

[1]: http://www.astropy.org/
[2]: http://numpy.scipy.org/

Optional Dependencies
------------
[scipy][1]

Scipy is used to do the interpolation regridding required if 
one wants to rescale the velocity axis.

[1]: http://www.scipy.org/


Installation
------------

    python setup.py install

Example usage
-------------

```python
import fits2itk

	# convert a FITS file using the default parameters
inputfile = "ngc1333_co.fits"
outputfile = "ngc1333_co.nrrd"

fits2itk.convert(inputfits,outputfile)

	#Or rescale the data and velocity scale relative to spatial
fits2itk.convert("13co10_done.fits","output.nrrd",data_scale=10,velocity_scale=2.)

	# read in the nrrd file to examine it
readdata, options = fits2itk.read(filename)
print readdata.shape
print options
```
Advanced usage
-------------
If all your datasubes are fairly homogeneous, you can put them 
all on the same scale. Currently this requires editing fits2itk.py
manually to set c_dict parameters (defaults only sensible for test datasets)

In the following there are two cubes with different spatial/spectral resolution
and only partially overlapping in space. With the use_conv flag the dimensions
are rescaled so that they will properly register when imported into Slicer3D 
(other 3D software not tested). The c18o32 file has velocities in km/s, while
the 13co10 file has velocities in m/s, so velocity_scale is used to account for 
this.

```python
import fits2itk
fits2itk.convert("ngc1333_c18o32.fits","c18o32.nrrd",velocity_scale=1000.,use_conv=True)
fits2itk.convert("ngc1333_13co10.fits","13co10.nrrd",velocity_scale=1.,use_conv=True)
```
License
-------

See LICENSE.
