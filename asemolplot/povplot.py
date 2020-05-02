from ase import io

import mcol # https://github.com/mwinokan/MPyTools
import mout # https://github.com/mwinokan/MPyTools

from . import styles

isPovLoaded = False

def loadPov(verbosity=1,purge=True,anaconda=False):
  import module # https://github.com/mwinokan/MPyTools

  # load the correct modules for ASE/PoV-Ray
  if (purge):
    module.module('purge')
  module.module('--expert','load','Boost/1.63.0-intel-2017a-Python-2.7.13')
  module.module('--expert','load','zlib/1.2.8-intel-2016a')
  module.module('--expert','load','libpng/1.6.24-intel-2016a')
  module.module('--expert','load','libjpeg-turbo/1.5.0-intel-2016a')
  module.module('--expert','load','LibTIFF/4.0.6-intel-2016a')
  if anaconda: module.module('--expert','load','anaconda3/2019.03')

  if (verbosity > 0):
    mout.out("PoV-Ray dependencies loaded.",
             printScript=True,)

  global isPovLoaded 
  isPovLoaded = True

def makePovImage(filename,image,verbosity=1,rmPovFiles=True,bonds=False,bondradius=1.1,forceLoad=False,**style):
  if (not isPovLoaded or forceLoad):
    loadPov(verbosity=verbosity-1)

  if (verbosity > 0):
    mout.out("processing "+mcol.file+
             filename+".pov"+
             mcol.clear+" ... ",
             printScript=True,
             end='') # user output
    
  if (not style['drawCell']):
    image.set_cell([0,0,0])
  del style['drawCell']

  if (bonds):
    from ase.io.pov import get_bondpairs, set_high_bondorder_pairs
    bondpairs = get_bondpairs(image, radius=bondradius)
    if (len(bondpairs) > 5000):
      mout.warningOut("Too many bondpairs ("+str(len(bondpairs))+
                      "), not drawing bonds!",end=' ')
    else:
      style['bondatoms'] = bondpairs

  io.write(filename+'.pov',image,
    run_povray=True,
    camera_type='perspective',
    **style)

  if (rmPovFiles):
    import os
    os.system("rm "+filename+".ini")
    os.system("rm "+filename+".pov")

  if (verbosity > 0):
    mout.out("Done.") # user output

def makePovImages(filename,subdirectory="pov",interval=1,verbosity=1,rmPovFiles=True,bonds=False,bondradius=1.1,filenamePadding=4,forceLoad=False,index=":",**style):
  if (not isPovLoaded or forceLoad):
    loadPov(verbosity=verbosity-1)

  import os
  
  os.system("mkdir -p "+subdirectory)
  os.system("rm "+subdirectory+"/* 2> /dev/null")

  if index != ":":
    image = io.read(filename,index=index)
    makePovImage(subdirectory+"/"+str(index).zfill(filenamePadding),image,verbosity=verbosity-1,bonds=bonds,bondradius=bondradius,rmPovFiles=False,forceLoad=forceLoad,**style)
  else:
    traj = io.read(filename,index=index)

    if verbosity > 0:
      mout.varOut("Images in trajectory",len(traj))
    
    for n, image in enumerate(traj):
      if (n % interval != 0 and n != 100):
        continue

      makePovImage(subdirectory+"/"+str(n).zfill(filenamePadding),image,verbosity=verbosity-1,bonds=bonds,bondradius=bondradius,rmPovFiles=False,forceLoad=forceLoad,**style)

  if (rmPovFiles):
    os.system("rm "+subdirectory+"/*.ini")
    os.system("rm "+subdirectory+"/*.pov")

# Using ImageMagick (artefacting!):
def makePovAnimationIM(filename,subdirectory="pov",interval=1,verbosity=1,**style):
  if (not isPovLoaded or forceLoad):
    loadPov(verbosity=verbosity-1)

  import os
  import module # https://github.com/mwinokan/MPyTools

  makePovImages(filename,subdirectory=subdirectory,interval=interval,verbosity=verbosity-1,**style)

  module.module('--expert','load','ImageMagick/7.0.3-1-intel-2016a')
  if (verbosity > 0):
    mout.out("ImageMagick loaded.",printScript=True)

  if (verbosity > 0):
    mout.out("creating "+mcol.file+
         "animation.gif"+
         mcol.clear+" ... ",
         printScript=True,
         end='') # user output
  os.system("convert -delay 10 "+subdirectory+"/*.png -fill white -opaque none -loop 1 "+subdirectory+".gif")
  if (verbosity > 0):
    mout.out("Done.") # user output

# Using imageio
# https://stackoverflow.com/questions/753190/programmatically-generate-video-or-animated-gif-in-python
def makePovAnimation(filename,subdirectory="pov",interval=1,gifstyle=styles.gif_standard,verbosity=1,forceLoad=False,useExisting=False,dryRun=False,**plotstyle):
  if (not isPovLoaded or forceLoad):
    loadPov(verbosity=verbosity-1)

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
      makePovImages(filename,subdirectory=subdirectory,interval=interval,verbosity=verbosity-1,**plotstyle)
    else:
      # Generate just the first image
      makePovImages(filename,subdirectory=subdirectory,interval=interval,verbosity=verbosity-1,index=0,**plotstyle)
    
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

def crop(filename,width=500,height=500,xshift=0,yshift=0,verbosity=1):
  import os

  import module # https://github.com/mwinokan/MPyTools
  module.module('--expert','load','ImageMagick/7.0.3-1-intel-2016a')
  global isPovLoaded
  isPovLoaded = False
  if (verbosity > 0):
    mout.out("ImageMagick loaded.",printScript=True)

  os.system("convert "+filename+
            " -crop "+str(width)+
            "x"+str(height)+
            "+"+str(xshift)+
            "+"+str(yshift)+
            " "+filename)
