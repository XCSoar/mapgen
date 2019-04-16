import os
import math
import subprocess
from zipfile import ZipFile, BadZipfile

from xcsoar.mapgen.georect import GeoRect
from xcsoar.mapgen.filelist import FileList

__cmd_gdalwarp = 'gdalwarp'
__use_world_file = True

'''
EU-DEM terrain importer. EU-DEM terrain must be downloaded under <dir_data>/eu-dem, like:
<dir_data> % ls eu-dem/eu_dem*
eu-dem/eu_dem_v11_E40N40.TFw          eu-dem/eu_dem_v11_E40N50.TFw
eu-dem/eu_dem_v11_E40N40.TIF          eu-dem/eu_dem_v11_E40N50.TIF
eu-dem/eu_dem_v11_E40N40.TIF.aux.xml  eu-dem/eu_dem_v11_E40N50.TIF.aux.xml
eu-dem/eu_dem_v11_E40N40.TIF.ovr      eu-dem/eu_dem_v11_E40N50.TIF.ovr
eu-dem/eu_dem_v11_E40N40.zip          eu-dem/eu_dem_v11_E40N50.zip
'''

'''
 2) Merge tiles into big tif, Resample and Crop merged image
    gdalwarp
    -r cubic
        (Resampling method to use. Cubic resampling.)
    -tr $degrees_per_pixel $degrees_per_pixel
        (set output file resolution (in target georeferenced units))
    -wt Int16
        (Working pixel data type. The data type of pixels in the source
         image and destination image buffers.)
    -dstnodata -31744
        (Set nodata values for output bands (different values can be supplied
         for each band). If more than one value is supplied all values should
         be quoted to keep them together as a single operating system argument.
         New files will be initialized to this value and if possible the
         nodata value will be recorded in the output file.)
    -te $left $bottom $right $top
        (set georeferenced extents of output file to be created (in target SRS))
    a.tif b.tif c.tif ...
        (Input files)
    terrain.tif
        (Output file)
'''
def __create(dir_temp, tiles, arcseconds_per_pixel, bounds):
    print('Resampling terrain...')
    output_file = os.path.join(dir_temp, 'terrain.tif')
    degree_per_pixel = float(arcseconds_per_pixel) / 3600.0

    args = [__cmd_gdalwarp,
            '-wo', 'NUM_THREADS=ALL_CUPS',
            '-t_srs', 'EPSG:4326',
            '-r', 'cubic',
            '-tr', str(degree_per_pixel), str(degree_per_pixel),
            '-wt', 'Int16',
            '-dstnodata', '-31744', '-multi']

    if __use_world_file == True:
        args.extend(['-co', 'TFW=YES'])

    args.extend(['-te', str(bounds.left),
                str(bounds.bottom),
                str(bounds.right),
                str(bounds.top)])

    args.extend(tiles)
    args.append(output_file)

    subprocess.check_call(args)

    return output_file

'''
 3) Convert to GeoJP2 with GDAL
'''
def __convert(dir_temp, input_file, rc):
    print('Converting terrain to JP2 format...')
    output_file = os.path.join(dir_temp, 'terrain.jp2')

    args = ['gdal_translate',
            '-of', 'JP2OpenJPEG',
            '-co', 'BLOCKXSIZE=256',
            '-co', 'BLOCKYSIZE=256',
            '-co', 'QUALITY=95',
            '-ot', 'Int16',
            input_file,
            output_file]

    subprocess.check_call(args)

    output = FileList()
    output.add(output_file, False)

    world_file_tiff = os.path.join(dir_temp, "terrain.tfw")
    world_file = os.path.join(dir_temp, "terrain.j2w")
    if __use_world_file and os.path.exists(world_file_tiff):
        os.rename(world_file_tiff, world_file)
        output.add(world_file, True)

    return output

def __cleanup(dir_temp):
    for file in os.listdir(dir_temp):
        if  file.endswith(".tif") and (file.startswith("srtm_") or
                                       file.startswith("terrain")):
            os.unlink(os.path.join(dir_temp, file))

def create(bounds, arcseconds_per_pixel, downloader, dir_temp, dir_data):
    # calculate height and width (in pixels) of map from geo coordinates
    px =  round((bounds.right - bounds.left) * 3600 / arcseconds_per_pixel)
    py =  round((bounds.top - bounds.bottom) * 3600 / arcseconds_per_pixel)
    # round up so only full jpeg2000 tiles (256x256) are used
    # works around a bug in openjpeg 2.0.0 library
    px = (int(px / 256) + 1) * 256
    py = (int(py / 256) + 1) * 256
    # and back to geo coordinates for size
    bounds.right = bounds.left + (px * arcseconds_per_pixel / 3600)
    bounds.bottom = bounds.top - (py * arcseconds_per_pixel / 3600)

    # Make sure the tiles are available
    eudem_parent = os.path.join(dir_data, 'eu-dem')
    tiles = [os.path.join(eudem_parent, f) for f in os.listdir(eudem_parent) if f.endswith('TIF')]
    if len(tiles) < 1:
        return FileList()

    try:
        terrain_file = __create(dir_temp, tiles, arcseconds_per_pixel, bounds)
        return __convert(dir_temp, terrain_file, bounds)
    finally:
        __cleanup(dir_temp)
