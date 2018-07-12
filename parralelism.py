import json
import fiona
from shapely.geometry import shape, LineString, mapping, Point, MultiPoint, Polygon, MultiPolygon
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
bounding_box = multi_line.bounds
y = (bounding_box[3]-bounding_box[1])
x = (bounding_box[2]-bounding_box[0])
tmpx = bounding_box[0]
tmpy = bounding_box[1]
polygons = []
i=0
while tmpx < bounding_box[2]:
    tmpy = bounding_box[1]
    while tmpy < bounding_box[3]:
        polygons.append(Polygon([(tmpx, tmpy), (tmpx, tmpy + 1/111), (tmpx + 1/111, tmpy + 1/111), (tmpx + 1/111, tmpy)]))
        tmpy += 1/111
        i += 1
    tmpx += 1/111
# mp = MultiPolygon(polygons)
# dict = {}

for name in names:
    gjs = get_geojson('./points/' + name)
    if name == 'attraction':
        tmp = get_all_points(multi_line, gjs, 0.075)
    else:
        tmp = get_all_points(multi_line, gjs, 0.025)
    distances = []
    size = len(tmp)
    for polygon in polygons:
        distance = 0
        for val in tmp:
            distance += 1 / (val.distance(polygon)**5 + 1)
        distances.append(distance)
    print(max(distances))
    print(min(distances))
    # create_shp(name, tmp)

schema = {'geometry': 'MultiPolygon',
          'properties': {'id': 'int'}}

with fiona.open('test.shp', 'w', 'ESRI Shapefile', schema, encoding='utf-8') as c:
    c.write({'geometry':  mapping(mp),
                     'properties': {
                         'id' : 3}})


