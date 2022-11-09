# https://github.com/yohman/workshop-remote-sensing/blob/main/Remote%20Sensing%20Camp.ipynb

import pandas as pd
import geopandas as gpd

#earth engine
import ee

from IPython.display import Image, display

import urllib.request
from PIL import Image as IMG
import folium
from folium_fx import *

# earthengin auth
#ee.Authenticate()

ee.Initialize()

# coordinates of the camp fire
lat = 39.810278
lon = -121.437222

# point of interest
poi = ee.Geometry.Point(lon, lat)

#range to filter (se prendo un solo giorno potrei avere delle nuvole che bloccano la visuale)
start_date = '2018-10-01'
end_date = '2019-01-31'

# get satellite data
landsat = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')\
            .filterBounds(poi)\
            .filterDate(start_date, end_date)

# # of images
print('Total # of images: ', landsat.size().getInfo())

# print(landsat.first().getInfo())

# what about cloud cover of our first image?
print(landsat.first().get('CLOUD_COVER').getInfo())
# when was this image taken?
print(landsat.first().get('DATE_ACQUIRED').getInfo())

# bands
bands = landsat.first().bandNames().getInfo()

# put the images in a list
landsat_list = landsat.toList(landsat.size())

# Define a region of interest with a buffer zone of 20 km
roi = poi.buffer(20000) # meters

# set parameters for the images
parameters = {
                'min': 7000,
                'max': 16000,
                'dimensions': 800, # square size in pixels
                'bands': ['SR_B4', 'SR_B3', 'SR_B2'], # bands to display (r,g,b)
                'region':roi
             }

# create empty data container
data = []

# loop through each image to display it
for i in range (landsat.size().getInfo()):
    # when was the image taken?
    date = ee.Image(landsat_list.get(i)).get('DATE_ACQUIRED').getInfo()
    # cloud cover
    cloud = ee.Image(landsat_list.get(i)).get('CLOUD_COVER').getInfo()

    print('Image #', i, date, 'Cloud cover:', cloud)

    # display image jupiter notebook
    # display(Image(url = ee.Image(landsat_list.get(i)).getThumbURL(parameters)))

    # display and save image with pillow
    # url = ee.Image(landsat_list.get(i)).getThumbURL(parameters)
    # urllib.request.urlretrieve(url, "img{}".format(i))
    # img = IMG.open("img{}".format(i))
    # img.show()

    # data to list
    this_data=[i,date,cloud]
    data.append(this_data)



df = pd.DataFrame(data, columns=['Image #', 'Date', 'Cloud Cover'])
print(df)

# select images and zooming in
# create a list of images we want (before, during, after)
landsat_sequence = [0,2,5]

# The normalized difference vegetation index (NDVI) is a simple graphical indicator 
# that can be used to analyze remote sensing measurements, often from a space platform, 
# assessing whether or not the target being observed contains live green vegetation

# ndvi palette: red is low, green is high vegetation
palette = ['red', 'yellow', 'green']

ndvi_parameters = {'min': 0,
                   'max': 0.4,
                   'dimensions': 512,
                   'palette': palette,
                   'region': roi}

for i in landsat_sequence:
    # when was this image taken?
    date = ee.Image(landsat_list.get(i)).get('DATE_ACQUIRED').getInfo()
    
    # print some information
    print('Image #',i,date)
    
    # display the image
    # url=ee.Image(landsat_list.get(i)).normalizedDifference(['SR_B5', 'SR_B4']).getThumbUrl(ndvi_parameters)
    # urllib.request.urlretrieve(url, "imgNDVI{}".format(i))
    # img = IMG.open("imgNDVI{}".format(i))
    # img.show()

# interactive map
# m = folium.Map(location=[lat,lon])

# Add Earth Engine drawing method to folium
folium.Map.add_ee_layer = add_ee_layer

# Create a map
my_map = folium.Map(location=[lat, lon], zoom_start=10)

# Add a layer for each satellite image of interest (before, during and after)
for i in landsat_sequence:

    # when was this image taken?
    date = ee.Image(landsat_list.get(i)).get('DATE_ACQUIRED').getInfo()

    my_map.add_ee_layer(ee.Image(landsat_list.get(i)).normalizedDifference(['SR_B5', 'SR_B4']), 
                        ndvi_parameters, 
                        name=date)
    
# Add a layer control panel to the map
folium.LayerControl(collapsed = False).add_to(my_map)

my_map.save('InteractiveMap.html')