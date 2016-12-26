# -*- coding: utf-8 -*-
"""
Generating Lithopane from picture

@author: Benny Malengier
"""


from __future__ import print_function, division
import sys

from wand.image import Image
import subprocess

#first argument must be the image file
import argparse
parser = argparse.ArgumentParser(description='Image gilename to convert to lithopane')
parser.add_argument('imgfilename', help='filename of the image')
parser.add_argument('-i', '--info', action='store_true',
                    help="show information about the image like size")
parser.add_argument('-w', '--width', help="Width of the printed lithopane in mm. Default 50mm")

parser.add_argument('-r', '--resolution', help="Resolution of 3D print: 1 pixel=resolution in mm. Default: 1. (1pixel=1mm)")

inputdata = parser.parse_args() #parse arg from sys.argv


imgfilename = inputdata.imgfilename
info = inputdata.info
width = inputdata.width
if width is None:
    width = 50
else:
    width = float(width)
    
resolution = inputdata.resolution
if resolution is None:
    resolution = 1.  #mm for a pixel
else:
    resolution = float(resolution)

import os.path
if not os.path.isfile(imgfilename):
    print("Given file ", imgfilename, "NOT found. Exiting ...")
    sys.exit(0)

with Image(filename=imgfilename) as img:
    # print the size first    
    size = img.size  
    print("Size of image is:", size)
    #if not size[0] == size[1]:
    #    print('Error, square image required!')
    #    sys.exit(0)
    widthpximg, heightpximg = size
    #0.25mm resolution needed for 3D printer so this is pixels
    widthpx = width/resolution
    scaling = widthpx / widthpximg
if info:
    sys.exit(0)

#derived value
height = heightpximg/widthpximg*width

#with Image(filename=imgfilename) as img:
#    # print the size first  
#    #resize with this scaling
#    img.resize(int(widthpximg*scaling), int(heightpximg*scaling))
#    
#    img.format = 'png'
#    # grayscale it
#    img.type = 'grayscale'
#    # negative needed (only present in version 0.3.8)
#    #img.negate(True)
#    img.save(filename='out.png')

#params = ['-depth', '8', 'gray:out1.raw']
returnid = subprocess.call(["convert", imgfilename,  
                            '-type', 'Grayscale','-negate', 
                            '-resize', str(int(widthpximg*scaling)) + 'x' + 
                                 str(int(heightpximg*scaling)), 'out1.png'])


#returnid = subprocess.call(["convert", imgfilename,  
#                            '-type', 'Grayscale','-negate', 
#                            '-resize', str(int(widthpximg*scaling)) + 'x' + 
#                                 str(int(heightpximg*scaling)), '-depth', '8',
#                            'gray:out.raw'])
#                            
#with open('out1.raw','rb') as fin:
    
#
scadfile = """
image_file = "out1.png";
length = %(height)f;
width = %(width)f;
x_scale = %(scale)f;
y_scale = %(scale)f;
layer_height = 0.2;
number_of_layers = 12;

// png height map is 100 high, we map this to 0-1, and the height we want.
height = layer_height*number_of_layers/100;

include_frame = "no"; // [yes, no]
include_hole = "no"; // [yes, no]
hole_diameter = 10;

/* [Hidden] */

// base (white) will always be 2 layers thick
min_layer_height = layer_height*2;
hole_radius = hole_diameter/2;

lithopane(height, width, x_scale, y_scale);

module lithopane(height, width, x_scale, y_scale) {
    union() {
        // take just the part of surface we want
        //difference() {
            translate([0, 0, min_layer_height]) scale([x_scale,y_scale,height]) surface(file=image_file, center=true, convexity=5);
       //     //cut off everything under 0
       //     translate([0,0,-(height+min_layer_height)]) linear_extrude(height=height+min_layer_height) square([width, height], center=true);
       // }
        //add a solid base of 2 layers high and extra 4 mm
        linear_extrude(height=layer_height*2) square([width+4, height+4], center=true);

        //add a more solid frame
        if (include_frame == "yes") {
            linear_extrude(height=height+min_layer_height) {
                difference() {
                    union() {
                        square([width+4, height+4], center=true);
                        if (include_hole == "yes") {
                            translate([0, height/2+hole_radius+2, 0]) circle(r=hole_radius+5);
                        }
                    }
                    union() {
                        square([width, height], center=true);
                        if (include_hole == "yes") {
                            translate([0, height/2+hole_radius+2, 0]) circle(r=hole_radius);
                        }
                    }
                }
            }
        }
    }
}
""" % {'width': width, 'height': height,
       'scale': width/widthpx}

#write out scad file
with open('lithopane.scad', 'w') as fscad:
    fscad.write(scadfile)
print ("To generate a box for this lithopane on lasercutter with kerf 0.16mm in material of 3mm, use following command")
print ("")
print ("python generate_squarebox.py -W %(widthbox)f -H %(heightbox)f -D %(depthbox)f "
        "-m 5 -t 3 -k 0.16 -o --recthole2 %(width)f,%(height)f lithobox" % {
            'widthbox'  : 20,    # 2cm 
            'heightbox' : width + 15,
            'depthbox'  : height + 15,
            'width'     : width,
            'height'    : height,
            })

print ("")
#call scad
print ("Starting openscad stl generation. This can take a while!")
returnid = subprocess.call(["/home/benny/git/openscad/openscad", '-o', 'lithopane.stl', 'lithopane.scad'])
print ("Generation finished. Stl in lithopane.stl" )
