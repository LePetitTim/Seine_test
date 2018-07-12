import json
import fiona
from shapely.geometry import shape, LineString, mapping, Point, MultiPoint
from shapely.ops import linemerge, cascaded_union
import os


def get_all_points(line, dict_point, distance):
    tab = []
    for i, point in enumerate(dict_point['features']):
        if point['geometry']['type'] == 'Point':

            if shape(point['geometry']).distance(line) < distance:
                # a peu près 2km5
                tab.append(shape(point['geometry']))
    return tab


def create_shp(name, mp):
    schema_point = {'geometry': 'MultiPoint',
                    'properties': {
                        'id': 'int'}}
    with fiona.open('./shp_files/' + name + '.shp', 'w', 'ESRI Shapefile', schema_point, encoding='utf-8') as c:
        c.write({'geometry': mapping(MultiPoint(mp)),
                 'properties': {
                     'id': 3}})


def get_geojson(name):
    with open(name + '.geojson') as json_data:
        return json.load(json_data)


names = [os.path.splitext(each)[0] for each in os.listdir('./points') if each.endswith('.geojson')]

with open('seine.geojson') as json_data:
    seine = json.load(json_data)

seine_geom_l = []
seine_geom_ml = []

for i, line in enumerate(seine['features']):
    if line['geometry']['type'] in ('LineString'):
        seine_geom_l.append(shape(line['geometry']))
    if line['geometry']['type'] in ('MultiLineString'):
        seine_geom_ml.append(shape(line['geometry']))

multi_line = [linemerge(seine_geom_l)]
multi_line.extend(seine_geom_ml)
multi_line = cascaded_union(multi_line)

for name in names:
    gjs = get_geojson('./points/' + name)
    if name == 'attraction':
        tmp = get_all_points(multi_line, gjs, 0.075)
    else:
        tmp = get_all_points(multi_line, gjs, 0.025)
    create_shp(name, tmp)

schema = {'geometry': 'MultiLineString',
          'properties': {'id': 'int'}}

with fiona.open('seine.shp', 'w', 'ESRI Shapefile', schema, encoding='utf-8') as c:
    c.write({'geometry':  mapping(multi_line),
                     'properties': {
                         'id' : 3}})


