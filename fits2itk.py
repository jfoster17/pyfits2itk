#!/usr/bin/env python
# encoding: utf-8
"""
fits2itk.py

Convert a fits file to NRRD for use in Slicer3D

Assumes that the order of axes in the FITS file 
is RA, Dec, Velocity.

Example Use
-----------
import fits2itk

# convert a FITS file using the default parameters
inputfile = "ngc1333_co.fits"
outputfile = "ngc1333_co.nrrd"

fits2itk.convert(inputfits,outputfile)



"""

import nrrd
from astropy.io import fits
import numpy as np

def convert(inputfile,outputfile,data_scale=1.,velocity_scale=False,use_conv=False):
    """
    Parameters
    ----------

    data_scale: Constant value to rescale the data, optional
        A value by which to scale the intensity of the cube,
        for instance to put it in useful units.
    
    velocity_scale: Relative scale for the velocity axis, optional
        By default, the velocity axis has the same scale as the 
        spatial axes. If set to "auto" then the velocity axis
        is rescaled/regridded to have the same length as the shortest 
        spatial axis. Can also be used to set the scaling manually. 
        If your velocity axis is 10 times longer than your spatial 
        axes, then the auto default will use velocity_scale=0.1 to 
        match the axes. Setting velocity_scale=1 preserves the 
        relative scales.
        
    use_conv: EXPERIMENTAL! Use a fixed convention for conversion.
        Use some fixed values for the conversion of pixels
        to millimeters. This allows one to convert multiple
        different cubes/images and overlay them in Slicer3D 
        without needing to regrid/interpolate them ahead of time.
        Currently EXPERIMENTAL and assumes RA/Dec/Vel
        Vel can be in km/s or m/s. Use velocity_scale to 
        manually specify (i.e. use velocity_scale = 1000. for
        the cubes in km/s and velocity_scale = 1. for the cubes
        in m/s.). Alwas specify velocity_scale when using this
        option.
        
    """
    
    d,h = fits.getdata(inputfile,header=True)
    
    if data_scale:
        d *= data_scale
    if not velocity_scale: #Determine scale automatically
        velocity_scale = 1.
    elif velocity_scale == 'auto':
        min_spatial = np.min(h['NAXIS1'],h['NAXIS2'])
        vel_length = h['NAXIS3']
        velocity_scale = min_spatial/vel_length
    if velocity_scale != 1 and not use_conv: #regrid velocity
        #This really isn't necessary or desireable. We could
        #just change the velocity scaling in the NRRD file
        #like we do for use_conv
        import pycongrid
        d = pycongrid.congrid(d,(h['NAXIS3']*velocity_scale,
                                 h['NAXIS2'],h['NAXIS1']),
                                 method='spline')
    
    
    #Assume FITS order is RA,Dec,Velocity
    #Numpy order is Velocity, Dec, RA
    #Slicer wants RA, Velocity, Dec
    d = np.swapaxes(d,0,1)
    d = np.swapaxes(d,0,2)
    #options = {'encoding':'raw'}
    
    #Want the _center_ of the cube at 0
    spaceorigin = -1*np.array(d.shape)/2.
    
    dra = 1.
    dvel = 1.
    ddec = 1.
    racenter = 0
    deccenter = 0
    velcenter = 0

    #This dictionary defines a convention for
    #aligning cubes. Make this a possible input
    #ra-mm is the conversion between mm and degrees of arc
    #A value of around 9000 works well for NGC1333
    #vel-mm is beween mm and m/s. 1 is fine for NGC1333
    #ra0,dec0,vel0 is the center in degrees and m/s.

    c_dict = {"ra-mm":9000.,
              "dec-mm":9000.,
              "vel-mm":1.,
              "ra0":52.24,
              "dec0":31.40,
              "vel0":7800.}

    
    if use_conv:
        dra  = h['CDELT1']*c_dict['ra-mm']
        ddec = h['CDELT2']*c_dict['dec-mm']
        dvel = h['CDELT3']*c_dict['vel-mm']*velocity_scale #Requires m/s
        ra0  = c_dict['ra0']
        dec0 = c_dict['dec']
        vel0 = c_dict['vel0']/velocity_scale
        racenter = (ra0-h['CRVAL1'])*np.cos(c_dict['dec0']*3.14/180.)/h['CDELT1']+h['CRPIX1']
        deccenter = -1*((dec0-h['CRVAL2'])/h['CDELT2']+h['CRPIX2'])
        velcenter = -1*((vel0-h['CRVAL3'])/(h['CDELT3'])+h['CRPIX3'])

    options = {}
    options['space'] = 'left-posterior-superior'
    options['space directions'] = [(-1*dra,0,0),(0,dvel,0),(0,0,ddec)]
    options['kinds'] = ['domain','domain','domain']
    spaceorigin[0] = racenter*dra
    spaceorigin[1] = velcenter*dvel
    spaceorigin[2] = deccenter*ddec
    options['space origin'] = spaceorigin

    #This could be an option. 'raw' allows import in paraview. 'gzip' files can
    #be a lot smaller, depending on the cube.
    options['encoding'] = 'raw'
    print(options)
    nrrd.write(outputfile,d,options=options)
    
def read(inputfile):
    data,options = nrdd.read(inputfile)
    return(data,options)