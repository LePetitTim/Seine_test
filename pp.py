import overpy

api = overpy.Overpass()
result = api.query("""
[out:json][timeout:500];
( area[name="Toulouse"]; )->.a;


  rel["network"="fr_tisseo"](area.a);(._;>;);

out body;
>;
""")
print(result.ways[0])