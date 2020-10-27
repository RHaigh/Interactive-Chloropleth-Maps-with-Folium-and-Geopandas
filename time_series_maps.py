import pandas as pd
import geopandas as gpd
import folium
import branca.colormap as cm
from folium.plugins import TimeSliderChoropleth
from typing import Iterable, Dict, Union, List

### Data Import ###
# As before, import the GeoDataFrame directly and specify the .shp layer
local_auth_shape = gpd.read_file('path_to_file/Counties_and_Unitary_Authorities__December_2017__Boundaries_GB-shp/Counties_and_Unitary_Authorities__December_2017__Boundaries_GB.shp')
local_auth_shape = local_auth_shape.rename(columns={'ctyua17nm': 'Region'})

# Read in the dataset and rename the utla name variable so we may join by a common column once again
local_auth_df = pd.read_csv('path/df-utla.csv')
local_auth_df = local_auth_df.rename(columns={'name': 'Region'})

### Data Wrangling ###
# Merge, ensuring output remains in geodataframe format
joined_df = local_auth_shape.merge(local_auth_df, on='Region')

# In our previous file, the date/time format was not important. If we are to use this for our new output then it must be specifically transformed:
joined_df['date'] = pd.to_datetime(joined_df['date']).astype(int) / 10**9
joined_df['date'] = joined_df['date'].astype(int).astype(str)

### Mapping ###
# Enter in scaling variables and colour scale for our legend. Use quantiles to define reactive max values
max_colour = joined_df['daily'].quantile((0.98)).tolist()
min_colour = 0
cmap = cm.linear.YlOrRd_09.scale(min_colour, max_colour)
joined_df['colour'] = joined_df['daily'].map(cmap)

# In order to help folium differentiate by date, even though the name variables are duplicated, we will break down our colours into a dictionary and append df
country_list = joined_df['Region'].unique().tolist()
country_idx = range(len(country_list))

style_dict = {}
for i in country_idx:
    country = country_list[i]
    result = joined_df[joined_df['Region'] == country]
    inner_dict = {}
    for _, r in result.iterrows():
        inner_dict[r['date']] = {'color': r['colour'], 'opacity': 0.7}
    style_dict[str(i)] = inner_dict

countries_df = joined_df[['geometry']]
countries_gdf = gpd.GeoDataFrame(countries_df)
countries_gdf = countries_gdf.drop_duplicates().reset_index()

# As with static maps, specify background tiles and initial location zoom
slider_map = folium.Map(min_zoom=4, zoom_start=6, max_bounds=True, tiles='cartodbpositron', location=[54.2331, -1.7578])

# Folium has an inherent function designed to facilitating this
time_element = TimeSliderChoropleth(
    data=countries_gdf.to_json(),
    styledict=style_dict,

).add_to(slider_map)

time_element = cmap.add_to(slider_map)
cmap.caption = "Daily Number of Confirmed Cases Feb-Oct 2020"

# Save output as html file
slider_map.save(outfile='TimeSliderChoropleth.html')
