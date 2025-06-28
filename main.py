import requests
import json
import folium
from folium.features import GeoJsonPopup

# load geojson from the deepstatemap api
geojson = requests.get('https://deepstatemap.live/api/history/last')
geojson_content = geojson.content.decode('utf-8').strip('\"')
geojson_content = json.loads(geojson_content)

# create map
maps = geojson_content['map']['features']

# replace {{ }} with { } to avoid jinja error
for feature in maps:
    if 'properties' in feature:
        for key in feature['properties']:
            val = feature['properties'][key]
            if isinstance(val, str):
                feature['properties'][key] = val.replace('{{', '{').replace('}}', '}')

# get number of polygons and create map
polygon_count = len(maps)
m = folium.Map(location=[49.7377041, 32.9794409], tiles="CartoDB dark_matter", zoom_start=6)

# go through all polygons
for i in range(polygon_count):
    geometry = maps[i]['geometry']
    type = geometry['type']

    if type != 'Point':
        continue
    
    # find the coordinates for the marker
    coordinates = geometry['coordinates']
    lat = coordinates[1]
    lon = coordinates[0]

    # get popup value and remove renundant text
    popup_value = maps[i]['properties']['name']
    names = popup_value.split('///')

    # keep ukrainian and english translation
    popup_value = f'{names[0]} - {names[1]}'

    # append a marker that shows the military division
    marker = folium.Marker(location=[lat, lon])
    marker.add_child(folium.Popup(popup_value, parse_html=True))

    marker.add_to(m)

# fill the polygons their appropriate color
def style_function(feature):
    return {
        'fillColor': feature['properties'].get('fill', '#3388ff'),
        'color': feature['properties'].get('stroke', '#000000'),
        'weight': 0.5,
        'fillOpacity': 0.5,
    }

# disregard points in the geojson so popups will work
features_without_points = [f for f in maps if f['geometry']['type'] != 'Point']

feature_collection = {
    'type': 'FeatureCollection',
    'features': features_without_points
}

# append geojson to the map
folium.GeoJson(
    feature_collection, 
    style_function=style_function, 
    name='Colored Polygons', 
    popup=GeoJsonPopup(
        fields=['name'],
        labels=False,
        localize=True,
        sticky=False,
        parse_html=True,
        max_width=300,
    )).add_to(m)

# save the map
m.save('ukraine_map.html')