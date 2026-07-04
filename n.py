import requests
import json
import geopandas as gpd

url = "https://overpass-api.de/api/interpreter"

query = """
[out:json][timeout:300];
area["name"="Polska"]->.poland;
(
  way["railway"="rail"](area.poland);
  way["railway"="narrow_gauge"](area.poland);
  way["railway"="light_rail"](area.poland);
  way["railway"="subway"](area.poland);
  way["railway"="tram"](area.poland);
  way["railway:track_ref"](area.poland);
  way["railway:ref"](area.poland);
  node["railway"="station"](area.poland);
  node["railway"="halt"](area.poland);
  node["railway"="stop"](area.poland);
);
out body;
>;
out skel qt;
"""

response = requests.post(url, data={'data': query})
data = response.json()

print(data)
