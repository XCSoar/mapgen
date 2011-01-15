import urllib
import os

from xcsoar.mapgen.georect import GeoRect
from xcsoar.mapgen.filelist import FileList
from xcsoar.mapgen.util import command

__cmd_ogr2ogr = "ogr2ogr"
__cmd_shptree = "shptree"

__vmap0_datasets = [
     { 'name': 'vmap0/eur', 'bounds': GeoRect( -35, 180, 90,  30) },
     { 'name': 'vmap0/noa', 'bounds': GeoRect(-180,   0, 90, -40) },
     { 'name': 'vmap0/sas', 'bounds': GeoRect(  25, 180, 50, -60) },
     { 'name': 'vmap0/soa', 'bounds': GeoRect(-180, 180, 30, -90) },
     ]

__osm_datasets = [
     { 'name': 'osm/planet', 'bounds': GeoRect(-180, 180, 90, -90) },
     ]

__layers = [
     { 'name':     'city_area',
       'datasets': __vmap0_datasets,
       'layer':    'pop-built-up-a',
       'range':    50,
       'color':    '223,223,0' },
     { 'name':     'water_area',
       'datasets': __vmap0_datasets,
       'layer':    'hydro-inland-water-a',
       'label':    'nam',
       'where':    'hyc=8',
       'range':    100,
       'color':    '85,160,255' },
     { 'name':     'water_line',
       'datasets': __vmap0_datasets,
       'layer':    'hydro-water-course-l',
       'label':    'nam',
       'where':    'hyc=8',
       'range':    7,
       'color':    '85,160,255' },
     { 'name':     'roadbig_line',
       'datasets': __osm_datasets,
       'layer':    'roadbig_line',
       'range':    15,
       'color':    '240,64,64',
       'pen_width': 3 },
     { 'name':     'roadmedium_line',
       'datasets': __osm_datasets,
       'layer':    'roadmedium_line',
       'range':    8,
       'color':    '240,64,64',
       'pen_width': 2 },
     { 'name':     'roadsmall_line',
       'datasets': __osm_datasets,
       'layer':    'roadsmall_line',
       'range':    3,
       'color':    '240,64,64' },
     { 'name':     'railway_line',
       'datasets': __vmap0_datasets,
       'layer':    'trans-railroad-l',
       'range':    10,
       'where':    'exs=28',
       'color':    '64,64,64'   },
     { 'name':     'citybig_point',
       'datasets': __osm_datasets,
       'layer':    'citybig_point',
       'label':    'name',
       'range':    15,
       'label_important_range': 10,
       'color':    '223,223,0'  },
     { 'name':     'citymedium_point',
       'datasets': __osm_datasets,
       'layer':    'citymedium_point',
       'label':    'name',
       'range':    10,
       'label_important_range': 3,
       'color':    '223,223,0'  },
     { 'name':     'citysmall_point',
       'datasets': __osm_datasets,
       'layer':    'citysmall_point',
       'label':    'name',
       'range':    3,
       'color':    '223,223,0'  },
     ]

def __filter_datasets(bounds, datasets):
     filtered = []
     for dataset in datasets:
         if bounds.intersects(dataset['bounds']):
             filtered.append(dataset)
     return filtered

def __create_layer_from_dataset(bounds, layer, dataset, append, downloader, dir_temp):
    if not isinstance(bounds, GeoRect):
        raise TypeError

    data_dir = downloader.retrieve_extracted(dataset['name'] + '.7z')

    print("Reading dataset " + dataset['name']  + " ...")
    arg = [__cmd_ogr2ogr]

    if append:
         arg.append("-update")
         arg.append("-append")

    if 'where' in layer:
         arg.extend(["-where", layer['where']])

    arg.extend(["-select", layer['label'] if 'label' in layer else ''])

    arg.extend(["-spat",
                str(bounds.left),
                str(bounds.bottom),
                str(bounds.right),
                str(bounds.top)])

    arg.append(dir_temp)
    arg.append(data_dir)

    arg.append(layer['layer'])
    arg.extend(['-nln', layer['name']])

    command(arg)

def __create_layer_index(layer, dir_temp):
    print("Generating index file for layer " + layer['name'] + " ...")
    arg = [__cmd_shptree]

    arg.append(os.path.join(dir_temp, layer['name'] + ".shp"))

    command(arg)

def __create_layer(bounds, layer, downloader, dir_temp, files, index):
    print("Creating topology layer " + layer['name'] + " ...")

    datasets = __filter_datasets(bounds, layer['datasets'])
    for i in range(len(datasets)):
        __create_layer_from_dataset(bounds, layer, datasets[i],
                                    i != 0, downloader, dir_temp)

    if os.path.exists(os.path.join(dir_temp, layer['name'] + '.shp')):
        __create_layer_index(layer, dir_temp)

        files.add(os.path.join(dir_temp, layer['name'] + '.shp'), False)
        files.add(os.path.join(dir_temp, layer['name'] + '.shx'), False)
        files.add(os.path.join(dir_temp, layer['name'] + '.dbf'), False)
        files.add(os.path.join(dir_temp, layer['name'] + '.prj'), False)
        files.add(os.path.join(dir_temp, layer['name'] + '.qix'), False)
        index.append(layer)

def __create_index_file(dir_temp, index):
    file = open(os.path.join(dir_temp, 'topology.tpl'), 'w')
    try:
         file.write("* filename, range, icon, label_index, r, g, b, pen_width, label_range, label_important_range\n")
         for layer in index:
              file.write(layer['name'] + ',' +
                         str(layer['range']) + ',,' +
                         ('1' if 'label' in layer else '') + ',' +
                         layer['color'] + ',' +
                         str(layer.get('pen_width', 1)) + ',' +
                         str(layer.get('label_range', layer['range'])) + ',' +
                         str(layer.get('label_important_range', 0)) + "\n")
    finally:
         file.close()
    return os.path.join(dir_temp, "topology.tpl")

def create(bounds, downloader, dir_temp):
    files = FileList()
    index = []
    for layer in __layers:
        __create_layer(bounds, layer, downloader, dir_temp, files, index)

    files.add(__create_index_file(dir_temp, index), True)
    return files
