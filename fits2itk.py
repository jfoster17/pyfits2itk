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
infile = "ngc1333_co.fits"
outfile = "ngc1333_co.nrrd"

fits2itk.convert(infile,outfile)

# convert a FITS file using parameters defined
# in an external file

fits2itk.convert(infile,outfile,vel_scale=1,use_conv="ngc1333_conv")

You can use the included strip_fourth_header.py to remove
any polarization axis present in your data.

Can be run from the command line as
python fits2itk.py -i ngc1333_co.fits -o ngc1333_co.nrrd

with the following options

-i : Infile       -- Input (FITS) file (req)
-o : Outfile      -- Output (NRRD) file (req)
-d : Datascale    -- Value by which to scale intensity (opt)
-v : Velscale     -- Relative scale for velocity axis (often < 1) (opt)
-u : Use Conv     -- Use the specified fixed/external conversion (opt)
-h : Help         -- Display this help

"""

import nrrd
from astropy.io import fits
import numpy as np
import importlib 
import sys,os,getopt

def convert(infile,outfile,data_scale=1.,vel_scale=False,use_conv=False):
    """
    Parameters
    ----------

    data_scale: Constant value to rescale the data, optional
        A value by which to scale the intensity of the cube,
        for instance to put it in useful units.
    
    vel_scale: Relative scale for the velocity axis, optional
        By default, the velocity axis has the same scale as the 
        spatial axes. If set to "auto" then the velocity axis
        is rescaled/regridded to have the same length as the shortest 
        spatial axis. Can also be used to set the scaling manually. 
        If your velocity axis is 10 times longer than your spatial 
        axes, then the auto default will use vel_scale=0.1 to 
        match the axes. Setting vel_scale=1 preserves the 
        relative scales.
        
    use_conv: EXPERIMENTAL! Use a fixed convention for conversion.
        Use values stored in an external file for the conversion of 
        pixels to millimeters. This allows one to convert multiple
        different cubes/images and overlay them in Slicer3D 
        without needing to regrid/interpolate them ahead of time.
        Currently EXPERIMENTAL and assumes RA/Dec/Vel
        Vel can be in km/s or m/s. Use vel_scale to 
        manually specify (i.e. use vel_scale = 1000. for
        the cubes in km/s and vel_scale = 1. for the cubes
        in m/s.). Always specify vel_scale when using this
        option.
        
    """
    
    d,h = fits.getdata(infile,header=True)
    
    if data_scale:
        d *= data_scale
    if not vel_scale: #Determine scale automatically
        vel_scale = 1.
    elif vel_scale == 'auto':
        min_spatial = np.min([h['NAXIS1'],h['NAXIS2']])
        vel_length = h['NAXIS3']
        vel_scale = min_spatial/vel_length
    
    dra = 1.
    dvel = 1.
    ddec = 1.
    racenter = h['NAXIS1']/2.
    deccenter = -1*h['NAXIS2']/2.
    velcenter = -1*h['NAXIS3']/2.
    
    if vel_scale != 1 and not use_conv: #regrid velocity
        dvel = dvel/vel_scale
        
    
    #Assume FITS order is RA,Dec,Velocity
    #Numpy order is Velocity, Dec, RA
    #Slicer wants RA, Velocity, Dec
    d = np.swapaxes(d,0,1)
    d = np.swapaxes(d,0,2)
    #options = {'encoding':'raw'}
    
    #Want the _center_ of the cube at 0
    spaceorigin = -1*np.array(d.shape)/2.

    if use_conv:
        # This line imports the dictionary defined in your convention 
        # file. The example included is called "ngc1333_conv"
        i = importlib.import_module(use_conv)
        dra  = h['CDELT1']*i.c_dict['ra-mm']
        ddec = h['CDELT2']*i.c_dict['dec-mm']
        dvel = h['CDELT3']*i.c_dict['vel-mm']*vel_scale #Requires m/s
        ra0  = i.c_dict['ra0']
        dec0 = i.c_dict['dec0']
        vel0 = i.c_dict['vel0']/vel_scale
        racenter = ((ra0-h['CRVAL1'])*np.cos(i.c_dict['dec0']*
                    np.pi/180.))/h['CDELT1']+h['CRPIX1']
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

    #This could be an option. 'raw' allows import in paraview. 
    #'gzip' files can be a lot smaller, depending on the cube.
    options['encoding'] = 'raw'
    print(options)
    nrrd.write(outfile,d,options=options)
    
def read(inputfile):
    data,options = nrdd.read(inputfile)
    return(data,options)

def main():
    """
    -i : Infile       -- Input (FITS) file
    -o : Outfile      -- Output (NRRD) file
    -d : Datascale    -- Value by which to scale intensity
    -v : Velscale     -- Relative scale for velocity axis (often < 1)
    -u : Use Conv     -- Use the specified fixed/external conversion
    -h : Help         -- Display this help
    """
    infile, outfile = False, False
    kwargs = {}
    kwargs["vel_scale"] = "auto"
    try:
        opts,args = getopt.getopt(sys.argv[1:],"i:o:d:v:u:h")
    except getopt.GetoptError,err:
        print(str(err))
        print(__doc__)
        sys.exit(2)
    for o,a in opts:
        if o == "-i":
            infile = a
        elif o == "-o":
            outfile = a
        elif o == "-d":
            kwargs["data_scale"] = float(a)
        elif o == "-v":
            kwargs["vel_scale"] = float(a)
        elif o == "-u":
            kwargs["use_conv"] = a
        elif o == "-h":
            print(__doc__)
            sys.exit(1)
        else:
            assert False, "unhandled option"
            print(__doc__)
            sys.exit(2)
    if not infile or not outfile:
        assert False, "Input or Output file not specified"
        print(__doc__)
        sys.exit(2)
    print(kwargs)
    convert(infile,outfile,**kwargs)
        
    
    
if __name__ == '__main__':
    main()
