# Bring in required libraries and ensure dependencies detailedi n the README have corrrectly installed. 
import pandas as pd
import geopandas as gpd
import folium

### Data Import ###
# Read in shapefile data. Geopandas requires a direct root path to your geodatabase and then the subsequent .shp layer
local_auth_shape = gpd.read_file('path_to_file/Counties_and_Unitary_Authorities__December_2017__Boundaries_GB-shp/Counties_and_Unitary_Authorities__December_2017__Boundaries_GB.shp').to_crs("EPSG:4326")
# We will rename the local authority name to something more easily remembered
local_auth_shape = local_auth_shape.rename(columns={'ctyua17nm': 'Region'})
# Then we will convert to decimal degrees
local_auth_shape = local_auth_shape.to_crs(epsg=3857)

# Next read in the sample dataset of coronavirus cases by utla contained within this repo. This data is publicly available and was obtained through the gov Covid API
local_auth_df = pd.read_csv('./df-utla.csv')
# We will rename our local authority name column so it matches our shapefile and we may use this as common column to merge
local_auth_df = local_auth_df.rename(columns={'name': 'Region'})
# Filter the dataset to a single chosen date, otherwise folium will attempt to map the entire dataset and will crash all but the most powerful of GIS computers
local_auth_df = local_auth_df[local_auth_df['date']=='2020-10-21']

### Data Wrangling ###
# We will merge our dataframe with the shapefile by a common column
joined_df = local_auth_shape.merge(local_auth_df, on='Region')
# Note that it is important to align the merge in this order as it tells pandas you wish the output to be a GeoDataFrame

### Mapping ###
# Folium will handle the mapping functions using its inherent Chloropleth class
# The Map() function requires an initial zoom level and lat/long location to open on, as with a leaflet map
mymap = folium.Map(location=[54.2331, -1.7578], zoom_start=7, tiles=None)
# TileLayer() allows us to choose the background map
folium.TileLayer('CartoDB positron',name="Light Map",control=False).add_to(mymap)

# We will define our bins as myscale and set these to reactively break down our data by quantiles
myscale = (joined_df['daily'].quantile((0,0.1,0.75,0.9,0.98,1))).tolist()

# Lastly, these arguments are fed into the Chloropleth() function
folium.Choropleth(
 geo_data=local_auth_shape,
 name='Choropleth',
 data=joined_df,
 columns=['Region','daily'],
 key_on="feature.properties.Region",
 fill_color='YlOrRd',
 threshold_scale=myscale,
 fill_opacity=0.5,
 line_opacity=0.2,
 legend_name='Daily Covid Cases by Local Authority',
 smooth_factor=0
).add_to(mymap)

### Output ###
# Your may save this folium map object as an html file by using:
mymap.save('./map.html')

# However, you may wish to customise it further. As it is in html format, we may inject html directly to customise:
loc = 'Covid Cases Within 24 Hours by Local Authority 2020-10-21'
title_html = '''
             <h3 align="center" style="font-size:16px"><b>{}</b></h3>
             '''.format(loc)

# Now we have defined a simple H3 title, we can add it to our map with the add_child() function:
mymap.get_root().html.add_child(folium.Element(title_html))

# And rewrite the output
mymap.save('./map.html')

# If you wish to save your output as a png or pdf image, then you will need to take a web shot of your html output. This can be done using selenium webdriver
import selenium.webdriver
from selenium.webdriver.chrome.options import Options

# You must download the correct webdriver and set its executable path
chrome_options = Options()
chrome_options.add_argument("--headless")
driver = selenium.webdriver.Chrome(options=chrome_options, executable_path=r"path_to_file/chromedriver")
driver.set_window_size(2500, 1500)  # choose a resolution
driver.get('file:///Users/richardhaigh/Downloads/map.html') # You must pass it the location of the html file when initialised
driver.save_screenshot('.map.png') # Enter your desired output location

# Any errors likely stem from a mis-aligned browser and webdriver

