#!/usr/bin/env python
# encoding: utf-8
"""
fits2itk.py
"""

import nrrd
import astropy

def convert(inputfile,outputfile):
    d,h = pyfits.getdata(inputfile,header=True)
    #Assume FITS order is RA,Dec,Velocity
    #Numpy order is Velocity, Dec, RA
    #Slicer wants RA, Velocity, Dec
    d = np.swapaxes(d,0,1)
    d = np.swapaxes(d,0,2)
    nrrd.write(outputfile,d)
    
    