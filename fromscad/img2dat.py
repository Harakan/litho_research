#!/usr/bin/env python

import image
import numpy as np

def load_image( infilename ) :
    img = image.open( infilename )
    img.load()
    data = np.asarray( img, dtype="float" )
    return data

def save_image( npdata, outfilename ) :
    img = Image.fromarray( np.asarray( np.clip(npdata,0,255), dtype="uint8"), "L" )
    img.save( outfilename )
