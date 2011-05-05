import os
import math
import subprocess
from zipfile import ZipFile, BadZipfile

from xcsoar.mapgen.georect import GeoRect
from xcsoar.mapgen.filelist import FileList

__cmd_geojasper = 'geojasper'
__cmd_gdalwarp = 'gdalwarp'
__use_world_file = True

__additional_tiles = [
    'srtm_01_00', 'srtm_40_-2', 'srtm_43_-2', 'srtm_47_-2', 
    'srtm_50_-2', 'srtm_53_-4', 'srtm_57_00', 'srtm_61_00', 
    'srtm_65_-2', 'srtm_69_-2', 'srtm_01_-1', 'srtm_40_-3', 
    'srtm_43_-3', 'srtm_47_-3', 'srtm_50_-3', 'srtm_54_00', 
    'srtm_57_-1', 'srtm_61_-1', 'srtm_65_-3', 'srtm_70_00',
    'srtm_01_-2', 'srtm_40_-4', 'srtm_43_-4', 'srtm_47_-4', 
    'srtm_50_-4', 'srtm_54_-1', 'srtm_57_-2', 'srtm_61_-2', 
    'srtm_66_00', 'srtm_70_-1', 'srtm_02_00', 'srtm_41_00', 
    'srtm_44_00', 'srtm_48_00', 'srtm_51_00', 'srtm_54_-2', 
    'srtm_57_-3', 'srtm_62_00', 'srtm_66_-1', 'srtm_70_-2',
    'srtm_02_-1', 'srtm_41_-1', 'srtm_44_-1', 'srtm_48_-1', 
    'srtm_51_-1', 'srtm_54_-3', 'srtm_58_00', 'srtm_62_-1', 
    'srtm_66_-2', 'srtm_71_00', 'srtm_03_00', 'srtm_41_-2', 
    'srtm_44_-4', 'srtm_48_-2', 'srtm_51_-2', 'srtm_55_00', 
    'srtm_58_-1', 'srtm_62_-2', 'srtm_66_-3', 'srtm_71_-1',
    'srtm_03_-1', 'srtm_41_-3', 'srtm_45_00', 'srtm_48_-3', 
    'srtm_52_00', 'srtm_55_-1', 'srtm_58_-2', 'srtm_63_00', 
    'srtm_67_00', 'srtm_71_-2', 'srtm_37_00', 'srtm_41_-4', 
    'srtm_45_-1', 'srtm_48_-4', 'srtm_52_-1', 'srtm_55_-2', 
    'srtm_58_-3', 'srtm_63_-1', 'srtm_67_-1', 'srtm_72_00',
    'srtm_38_00', 'srtm_42_00', 'srtm_45_-4', 'srtm_49_00', 
    'srtm_52_-2', 'srtm_55_-3', 'srtm_59_00', 'srtm_63_-2', 
    'srtm_67_-2', 'srtm_72_-1', 'srtm_39_00', 'srtm_42_-1', 
    'srtm_46_00', 'srtm_49_-1', 'srtm_52_-3', 'srtm_55_-4', 
    'srtm_59_-1', 'srtm_64_00', 'srtm_67_-3', 'srtm_72_-2',
    'srtm_39_-1', 'srtm_42_-2', 'srtm_46_-1', 'srtm_49_-2', 
    'srtm_52_-4', 'srtm_56_00', 'srtm_59_-2', 'srtm_64_-1', 
    'srtm_68_00', 'srtm_39_-3', 'srtm_42_-3', 'srtm_46_-3', 
    'srtm_49_-3', 'srtm_53_00', 'srtm_56_-1', 'srtm_59_-3', 
    'srtm_64_-2', 'srtm_68_-1', 'srtm_39_-4', 'srtm_42_-4', 
    'srtm_46_-4', 'srtm_49_-4', 'srtm_53_-1', 'srtm_56_-2', 
    'srtm_60_00', 'srtm_64_-3', 'srtm_68_-2', 'srtm_40_00', 
    'srtm_43_00', 'srtm_47_00', 'srtm_50_00', 'srtm_53_-2', 
    'srtm_56_-3', 'srtm_60_-1', 'srtm_65_00', 'srtm_69_00',
    'srtm_40_-1', 'srtm_43_-1', 'srtm_47_-1', 'srtm_50_-1', 
    'srtm_53_-3', 'srtm_56_-4', 'srtm_60_-2', 'srtm_65_-1', 
    'srtm_69_-1']

'''
 1) Retrieve tiles
'''
def __get_tile_name(lat, lon):
    col = int(math.floor(((lon + 180) / 5) + 1))
    row = int(math.floor((60 - lat) / 5))
    name = 'srtm_{0:02}_{1:02}'.format(col, row)
    if (col < 1 or col > 72 or row < 1 or row > 24) and (not name in __additional_tiles):
        raise RuntimeError('Coordinate out of bounds')
    return name

def __extract_tile(zip_file, dir_temp, filename):
    try:
        zip = ZipFile(zip_file, 'r')
    except BadZipfile:
        os.unlink(zip_file)
        raise RuntimeError('Decompression of the file {} failed.'.format(zip_file))
    zip.extract(filename + '.tif', dir_temp)
    zip.close()

def __retrieve_tile(downloader, dir_temp, lat, lon):
    filename = __get_tile_name(lat, lon)
    zip_file = downloader.retrieve('srtm3/{}.zip'.format(filename))
    print('Tile {} found inside zip file.'.format(filename))
    __extract_tile(zip_file, dir_temp, filename)
    return os.path.join(dir_temp, filename + ".tif")

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
    args = [__cmd_geojasper,
            '-f', input_file,
            '-F', output_file,
            '-T', 'jp2',
            '-O', 'rate=1.0',
            '-O', 'tilewidth=256',
            '-O', 'tileheight=256']

    if not __use_world_file:
        args.extend(['-O', 'xcsoar=1',
                     '-O', 'lonmin=' + str(rc.left),
                     '-O', 'lonmax=' + str(rc.right),
                     '-O', 'latmax=' + str(rc.top),
                     '-O', 'latmin=' + str(rc.bottom)])

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
    # Make sure the tiles are available
    tiles = __retrieve_tiles(downloader, dir_temp, bounds)
    if len(tiles) < 1:
        return FileList()

    try:
        terrain_file = __create(dir_temp, tiles, arcseconds_per_pixel, bounds)
        return __convert(dir_temp, terrain_file, bounds)
    finally:
        __cleanup(dir_temp)
