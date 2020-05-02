from ase import io

import mcol # https://github.com/mwinokan/MPyTools
import mout # https://github.com/mwinokan/MPyTools

from . import styles

def makeImage(filename,image,verbosity=1,**style):
  if (verbosity > 0):
    mout.out("creating "+mcol.file+
             filename+".png"+
             mcol.clear+" ... ",
             printScript=True,
             end='') # user output

  if not 'drawCell' in style:
    style['drawCell'] = False
  if not style['drawCell']:
    image.set_cell([0,0,0])
    style['show_unit_cell'] = 0
    # style['celllinewidth'] = 0
  if 'drawCell' in style:
    del style['drawCell']

  # print(style)

  # delete povray specific style parameters
  if 'canvas_width' in style:
    style['maxwidth'] = style['canvas_width']
    del style['canvas_width']
  if 'canvas_height' in style:
    del style['canvas_height']
  # if 'crop_xshift' in style:
  #   del style['crop_xshift']
  # if 'crop_yshift' in style:
  #   del style['crop_yshift']
  if 'celllinewidth' in style:
    del style['celllinewidth']
  # if 'transparent' in style:
  #   del style['transparent']

  io.write(filename+'.png',image,
    **style)
  
  if (verbosity > 0):
    mout.out("Done.") # user output

def makeImages(filename,subdirectory="amp",interval=1,verbosity=1,filenamePadding=4,index=":",**style):
  
  import os
  
  os.system("mkdir -p "+subdirectory)
  os.system("rm "+subdirectory+"/* 2> /dev/null")

  if index != ":":
    image = io.read(filename,index=index)
    makeImage(subdirectory+"/"+str(index).zfill(filenamePadding),image,verbosity=verbosity-1,**style)
  else:
    traj = io.read(filename,index=index)

    if verbosity > 0:
      mout.varOut("Images in trajectory",len(traj))
    
    for n, image in enumerate(traj):
      if (n % interval != 0 and n != 100):
        continue

      makeImage(subdirectory+"/"+str(n).zfill(filenamePadding),image,verbosity=verbosity-1,**style)

# Using imageio
# https://stackoverflow.com/questions/753190/programmatically-generate-video-or-animated-gif-in-python
def makeAnimation(filename,subdirectory="amp",interval=1,gifstyle=styles.gif_standard,verbosity=1,useExisting=False,dryRun=False,**plotstyle):
  
  if plotstyle == {}:
    plotstyle=styles.standard
  # print(plotstyle)

  import os
  import imageio

  cropping = False
  shifting = False

  # Set canvas sizes:
  canv_w = plotstyle["canvas_width"]
  if "canvas_height" in plotstyle:
    canv_h = plotstyle["canvas_height"]
    del plotstyle["canvas_height"]
  else:
    mout.errorOut("No canvas_height specified in plotstyle!",fatal=True)

  # Check if cropping:
  if "crop_w" in plotstyle and "crop_w" in plotstyle:
    cropping = True
    crop_w = plotstyle["crop_w"]
    crop_h = plotstyle["crop_h"]
  if "crop_w" in plotstyle: del plotstyle["crop_w"]
  if "crop_h" in plotstyle: del plotstyle["crop_h"]

  # Check if crop offset:
  if "crop_x" in plotstyle:
    shifting = True
    crop_x = plotstyle["crop_x"]
    crop_y = plotstyle["crop_y"]
  if "crop_x" in plotstyle: del plotstyle["crop_x"]
  if "crop_y" in plotstyle: del plotstyle["crop_y"]

  # Generate the PNG's
  if not useExisting:
    if (verbosity > 0):
      mout.out("generating "+mcol.file+
             subdirectory+"/*.png"+
             mcol.clear+" ... ",
             printScript=True,end='') # user output
    if (verbosity > 1):
      mout.out(" ")

    if not dryRun:
      # Generate all the images
      makeImages(filename,subdirectory=subdirectory,interval=interval,verbosity=verbosity-1,**plotstyle)
    else:
      # Generate just the first image
      makeImages(filename,subdirectory=subdirectory,interval=interval,verbosity=verbosity-1,index=0,**plotstyle)
    
    if (verbosity == 1):
      mout.out("Done.")

  # Load ImageMagick
  # if cropping or backwhite:
  import module # https://github.com/mwinokan/MPyTools
  ret = module.module('--expert','load','ImageMagick/7.0.3-1-intel-2016a')
  if ret == 0 and verbosity > 0:
    mout.out("ImageMagick loaded.",printScript=True)

  # Combine the images
  if (verbosity > 0):
    mout.out("loading "+mcol.file+
           subdirectory+"/*.png"+
           mcol.clear+" ... ",
           printScript=True,
           end='') # user output

  images = []

  # loop over all files in the subdirectory:
  for file in os.listdir(subdirectory):

    # get the relative path to the file:
    filename = subdirectory+"/"+file

    # check if the file is a PNG:
    if file.endswith(".png"):

      # run different IM commands depending on cropping and shifting:
      if not cropping and not shifting:
        os.system("convert "+filename+
                  " -background white -extent "+
                  str(canv_w)+"x"+
                  str(canv_h)+" "+
                  filename)
      elif cropping and not shifting:
        os.system("convert "+filename+
                  " -crop "+str(crop_w)+"x"+str(crop_h)+
                  " -background white -extent "+
                  str(crop_w)+"x"+
                  str(crop_h)+" "+
                  filename)
      elif shifting and not cropping:
        os.system("convert "+filename+
                  " -crop +"+str(crop_x)+"+"+str(crop_y)+
                  " -background white -extent "+
                  str(canv_w)+"x"+
                  str(canv_h)+" "+
                  filename)
      else:
        os.system("convert "+filename+
                  " -crop "+str(crop_w)+"x"+str(crop_h)+
                  "+"+str(crop_x)+"+"+str(crop_y)+
                  " -background white -extent "+
                  str(crop_w)+"x"+
                  str(crop_h)+" "+
                  filename)

      # Read in the image and append to the image array
      image = imageio.imread(filename)
      images.append(image)

  if (verbosity > 0) and not useExisting:
    mout.out("Done.") # user output

  if (verbosity > 0):
    mout.out("creating "+mcol.file+
           subdirectory+".gif"+
           mcol.clear+" ... ",
           printScript=True,
           end='') # user output

  # Generate the animated GIF:
  imageio.mimsave(subdirectory+".gif",images,**gifstyle)

  if (verbosity > 0):
    mout.out("Done.") # user output
