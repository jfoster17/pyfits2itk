#!/usr/bin/env python
# encoding: utf-8
"""
strip_fourth_fits_header.py

Radio datacubes often have a fourth
axis describing polarization. This
script just strips out the fourth
header to work with other scripts
like fits2itk.py

strip_fourth_fits_header.py infile outfile 1

clobber == 1 -> True (overwrites outfile if present)

"""
from astropy.io import fits
import numpy as np
import sys

def main():
    infile = sys.argv[1]
    outfile = sys.argv[2]
    try:
        clobber = sys.argv[3]
    except:
        clobber = False
    if clobber == 1:
        clobber = True
    strip(infile,outfile,clobber)


def trim_vel(infile,outfile,vmin,vmax):
    """
    Trim the velocity axis
    
    """
    d,h = fits.getdata(infile,header=True)
    d = d[vmin:vmax]
    h['CRPIX3'] = h['CRPIX3']-vmin
    fits.writeto(outfile,d,h,clobber=True)


def strip(infile,outfile,clobber=False):
    d,h = fits.getdata(infile,header=True)

    d = np.squeeze(d)

    h['NAXIS'] = 3
    try:
            del h['NAXIS4']
            del h['CTYPE4']
            del h['CRVAL4']
            del h['CDELT4']
            del h['CRPIX4']
            del h['CUNIT4']
    except:
            pass

    fits.writeto(outfile,d,h,clobber=clobber)


if __name__ == '__main__':
    main()
