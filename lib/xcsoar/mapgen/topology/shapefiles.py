import os
import subprocess
import json

from xcsoar.mapgen.util import slurp
from xcsoar.mapgen.georect import GeoRect
from xcsoar.mapgen.filelist import FileList

__cmd_ogr2ogr = 'ogr2ogr'
__cmd_shptree = 'shptree'

def __filter_datasets(bounds, datasets):
     filtered = []
     for dataset in datasets:
         if bounds.intersects(GeoRect(*dataset['bounds'])):
             filtered.append(dataset)
     return filtered

def __create_layer_from_dataset(bounds, layer, dataset, append, downloader, dir_temp):
    if not isinstance(bounds, GeoRect):
        raise TypeError

    data_dir = downloader.retrieve_extracted(dataset['name'] + '.7z')

    print('Reading dataset {} ...'.format(dataset['name']))
    arg = [__cmd_ogr2ogr]

    if append:
         arg.append("-update")
         arg.append("-append")

    if 'src_where' in layer:
         arg.extend(["-where", layer['src_where']])

    arg.extend(["-select", layer['src_label'] if 'src_label' in layer else ''])

    arg.extend(["-spat",
                str(bounds.left),
                str(bounds.bottom),
                str(bounds.right),
                str(bounds.top)])

    arg.append(dir_temp)
    arg.append(data_dir)

    arg.append(layer['src_layer'])
    arg.extend(['-nln', layer['name']])

    subprocess.check_call(arg)

def __create_layer_index(layer, dir_temp):
    print('Generating index file for layer {} ...'.format(layer['name']))
    subprocess.check_call([__cmd_shptree, os.path.join(dir_temp, layer['name'] + ".shp")])

def __create_layer(bounds, layer, datasets, downloader, dir_temp, files, index):
    print('Creating topology layer {} ...'.format(layer['name']))

    datasets = __filter_datasets(bounds, datasets)
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
                         ('1' if 'src_label' in layer else '') + ',' +
                         layer['color'] + ',' +
                         str(layer.get('pen_width', 1)) + ',' +
                         str(layer.get('label_range', layer['range'])) + ',' +
                         str(layer.get('label_important_range', 0)) + "\n")
    finally:
         file.close()
    return os.path.join(dir_temp, "topology.tpl")

def create(bounds, downloader, dir_temp):
     data = json.loads(slurp(downloader.retrieve('topology.json')))

     files = FileList()
     index = []
     for layer in data['layers']:
          __create_layer(bounds, layer, data['datasets'][layer['src_dataset']], downloader, dir_temp, files, index)

     files.add(__create_index_file(dir_temp, index), True)
     return files
