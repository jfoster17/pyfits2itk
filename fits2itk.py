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
        
    use_conv: Use a fixed convention for conversion.
        This convention defines a fixed a system for conversion
        1 arcsecond = 1 mm
        0.1 km/s = 1 mm
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
    
    if velocity_scale != 1 and not use_conv:
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
    
    spaceorigin = -1*np.array(d.shape)/2.
    
    dra = 1.
    dvel = 1.
    ddec = 1.
    racenter = 0
    deccenter = 0
    velcenter = 0
    
    
    if use_conv:
        dra = h['CDELT1']*60.*150.
        ddec = h['CDELT2']*60.*150.
        dvel = h['CDELT3']/100.*velocity_scale*100. #Requires m/s
        ra0 = 52.24
        dec0 = 31.4
        vel0 = 7800./velocity_scale
        racenter = (ra0-h['CRVAL1'])*np.cos(31.4*3.14/180.)/h['CDELT1']+h['CRPIX1']
        print(racenter)
        deccenter = -1*((dec0-h['CRVAL2'])/h['CDELT2']+h['CRPIX2'])
        print(deccenter)
        velcenter = -1*((vel0-h['CRVAL3'])/(h['CDELT3'])+h['CRPIX3'])
        #print(racenter,deccenter,velcenter)


    #We need to use the spaceorigin to align these cubes
    #This will have to be set in an external file or from the command line
    
    options = {}
    options['space'] = 'left-posterior-superior'
    options['space directions'] = [(-1*dra,0,0),(0,dvel,0),(0,0,ddec)]
    options['kinds'] = ['domain','domain','domain']
    #spaceorigin[0] = (-spaceorigin[0]- racenter)*dra
    #spaceorigin[1] = (-spaceorigin[1]- velcenter)*dvel
    #spaceorigin[2] = (-spaceorigin[2]- deccenter)*ddec

    spaceorigin[0] = racenter*dra
    spaceorigin[1] = velcenter*dvel
    spaceorigin[2] = deccenter*ddec

    
    options['space origin'] = spaceorigin
    options['encoding'] = 'raw'
    print(options)
    #options['space origin'] = [75,50,75]
    nrrd.write(outputfile,d,options=options)#,options=options)
    
def read(inputfile):
    data,options = nrdd.read(inputfile)
    return(data,options)