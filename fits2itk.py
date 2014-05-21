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

def convert(inputfile,outputfile,data_scale=1.,velocity_scale=False):
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
    
    if velocity_scale != 1:
        import pycongrid
        d = pycongrid.congrid(d,(h['NAXIS3']*velocity_scale,
                                 h['NAXIS2'],h['NAXIS1']),
                                 method='spline')
    
    
    #Assume FITS order is RA,Dec,Velocity
    #Numpy order is Velocity, Dec, RA
    #Slicer wants RA, Velocity, Dec
    d = np.swapaxes(d,0,1)
    d = np.swapaxes(d,0,2)
    #options = {}
    #options['space origin'] = [75,50,75]
    nrrd.write(outputfile,d)#,options=options)
    
def read(inputfile):
    data,options = nrdd.read(inputfile)
    return(data,options)