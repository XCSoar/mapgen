import os
import math
import subprocess
from zipfile import ZipFile, BadZipfile

from xcsoar.mapgen.georect import GeoRect
from xcsoar.mapgen.filelist import FileList

__cmd_geojasper = 'geojasper'
__cmd_gdalwarp = 'gdalwarp'
__use_world_file = True

'''
 1) Retrieve tiles
'''
def __get_tile_name(lat, lon):
    col = int(math.floor(((lon + 180) / 5) + 1))
    row = int(math.floor((60 - lat) / 5))
    return 'srtm_{0:02}_{1:02}'.format(col, row)

def __retrieve_tile(downloader, dir_temp, lat, lon):
    filename = __get_tile_name(lat, lon)
    tif_file = downloader.retrieve('srtm3/{}.tif'.format(filename))
    print('Tile {} found.'.format(filename))
    return tif_file

def __retrieve_tiles(downloader, dir_temp, bounds):
    '''
    Makes sure the terrain tiles are available at a certain location.
    @param downloader: Downloader
    @param dir_temp: Temporary path
    @param bounds: Bounding box (GeoRect)
    @return: The list of tile files
    '''
    if not isinstance(bounds, GeoRect):
        raise TypeError

    print('Retrieving terrain tiles...')

    # Calculate rounded bounds
    lat_start = int(math.floor(bounds.bottom / 5.0)) * 5
    lon_start = int(math.floor(bounds.left / 5.0)) * 5
    lat_end = int(math.ceil(bounds.top / 5.0)) * 5
    lon_end = int(math.ceil(bounds.right / 5.0)) * 5

    tiles = []
    # Iterate through latitude and longitude in 5 degree interval
    for lat in range(lat_start, lat_end, 5):
        for lon in range(lon_start, lon_end, 5):
            try:
                tiles.append(__retrieve_tile(downloader, dir_temp, lat, lon))
            except Exception as e:
                print('Failed to retrieve tile for {0:02}/{1:02}: {2}'.format(lat, lon, e))

    # Return list of available tile files
    return tiles

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
            '-r', 'cubic',
            '-tr', str(degree_per_pixel), str(degree_per_pixel),
            '-wt', 'Int16',
            '-dstnodata', '-31744']

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
 3) Convert to GeoJP2 with GeoJasPer
    geojasper
    -f blabla_cropped.tif
        (Input file name)
    -F terrain.jp2
        (Output file name)
    -T jp2
        (Output type)
    -O rate=0.1
        (Compression rate, 10 times)
    -O tilewidth=256
        (generate tiled image using tile width 256)
    -O tileheight=256
        (generate tiled image using tile height 256)
    -O xcsoar=1
        (???)
'''
def __convert(dir_temp, input_file, rc):
    print('Converting terrain to JP2 format...')
    output_file = os.path.join(dir_temp, 'terrain.jp2')

    args = ['gdal_translate',
            '-of', 'JP2OpenJPEG',
            '-co', 'BLOCKXSIZE=256',
            '-co', 'BLOCKYSIZE=256',
            '-co', 'QUALITY=95',
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

def create(bounds, arcseconds_per_pixel, downloader, dir_temp):
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
    tiles = __retrieve_tiles(downloader, dir_temp, bounds)
    if len(tiles) < 1:
        return FileList()

    try:
        terrain_file = __create(dir_temp, tiles, arcseconds_per_pixel, bounds)
        return __convert(dir_temp, terrain_file, bounds)
    finally:
        __cleanup(dir_temp)
