import numpy as np
import seaborn as sns
import folium
import geopandas as gpd
import rasterio
from rasterio import warp
from rasterio import windows
import affine
from shapely.geometry import Polygon
import plotly.graph_objects as go
import logging


class TreeCanopyCover:
    def __init__(self, filepath, resolution=1,
                min_lat=None, max_lat=None, min_long=None, max_long=None):
        self.src = rasterio.open(filepath)
        self.min_lat = min_lat
        self.max_lat = max_lat
        self.min_long = min_long
        self.max_long = max_long
        
        self.resolution = resolution
        self.window = self._calc_window()
        
        if min_lat is None: 
            self.transform_window = self.src.transform
            self.band = self.src.read(1)    
        else: 
            logging.warn('there are bugs in windowed transformation!')
            self.transform_window = windows.transform(self.window,self.src.transform)
            self.band = self.src.read(1, window=self.window)
        
        self.transform, self.width, self.height = self._calc_transform()
        self.array = self._reproject()
        
    def _calc_window(self):
        """Transform the specified lat/long into the row/col window"""
        if self.min_lat is None: 
            window = windows.Window(0, 0, self.src.shape[1], self.src.shape[0]) 
        else: 
            logging.warn('there are bugs in windowed transformation!')
            # TODO - I think the width and height of the window are switched?
            xs, ys = warp.transform({'init': 'epsg:4326'}, self.src.crs, [self.min_long, self.max_long], [self.max_lat, self.min_lat])
            top_left = (xs[0], ys[0]) * ~self.src.transform
            bottom_right = (xs[1], ys[1]) * ~self.src.transform
            width = bottom_right[1] - top_left[1] 
            height = bottom_right[0] - top_left[0]
            # HACK - the first *should* be correct, but I had to switch them to get it to work...
            # window = Window(top_left[0], top_left[1], width, height)
            window = windows.Window(top_left[0], top_left[1], height, width)
            # DEBUGGING
#             x, y = top_left * self.src.transform 
#             longs, lats = warp.transform(self.src.crs, {'init': 'epsg:4326'}, [x], [y])
#             top_left_latlong = (lats[0], longs[0])
        return window
        
    def _calc_transform(self):
        bbox = windows.bounds(self.window, self.transform_window)
        transform,width,height = warp.calculate_default_transform(self.src.crs, {"init":"epsg:4326"},
                                                                  self.window.width,self.window.height,
                                                                  left=bbox[0],bottom=bbox[1],
                                                                  right=bbox[2],top=bbox[3], 
                                                                 resolution=self.resolution)
        return transform,width,height
        
    def _reproject(self):
        out_array = np.ndarray((1, self.height, self.width))
        warp.reproject(self.band,
                   out_array,src_crs=self.src.crs,dst_crs={"init":"epsg:4326"},
                   src_transform=self.transform_window,
                   dst_transform=self.transform)
        return out_array
    
    def to_gpdf(self):
        gpdf = to_gpdf(self.array[0], self.transform)
        return gpdf

    def to_map(self):
        m = map_tcc(self.array[0], self.transform)
        return m

    def save_tif(self, filepath):
        profile = self.src.profile
        profile['crs'] = rasterio.crs.CRS({"init":"epsg:4326"})
        profile['transform'] = tcc.transform
        profile['height'] = tcc.array.shape[1]
        profile['width'] = tcc.array.shape[2]
        with rasterio.Env():
            # Write an array as a raster band to a new 8-bit file
            with rasterio.open(filepath, 'w', **profile) as dst:
                dst.write(self.array.astype(rasterio.uint8))


def to_gpdf(array: np.array, transform: affine.Affine):
    """There's gotta be a better way of doing this"""
    assert len(array.shape) == 2, 'only 2D arrays supported'
    resolution = transform.a
    rows, cols = np.indices(array.shape)  
    geoms = []
    vals = []
    for col,row in zip(np.ravel(cols), np.ravel(rows)):
        # NOTE - top_left is x,y
        top_left = transform * (col,row)
        latitude = top_left[1]
        longitude = top_left[0]

        geoms += [Polygon([top_left, 
                           (top_left[0]+resolution, top_left[1]),
                           (top_left[0]+resolution, top_left[1]-resolution),
                           (top_left[0], top_left[1]-resolution)])]
        # NOTE - out_array is index by (row,col) wherease it is transformed by (col,row)
        vals += [array[(row, col)]]

    gpdf = gpd.GeoDataFrame(vals, geoms, columns=['tcc'])
    gpdf.index.name = 'geometry'
    gpdf = gpdf.reset_index()
    return gpdf


def map_tcc(array: np.array, transform: affine.Affine):
    CENTER = (45, -100)
    m = folium.Map(location=CENTER,
                tiles='cartodbpositron',  # a "cleaner" base map
                    zoom_start=4)

    # Use the affine transformation to define the raster bounds in lat/long coords
    bounds_trans = (transform.c,
                transform.f + transform.e*array.shape[0],
                transform.c + transform.a*array.shape[1],
                transform.f)

    pal = sns.color_palette('Greens', n_colors=11)
    pal_rbg = []
    for t in pal:
        pal_rbg += [(t[0]*255, t[1]*255, t[2]*255)]
        
    def colorfun(x):
        if x > 100: 
            x = 0 # topcode since missingness is 255
        return pal_rbg[int(x/10)]

    image_overlay = folium.raster_layers.ImageOverlay(array,
                                                  [[bounds_trans[1],
                                                    bounds_trans[0]],
                                                   [bounds_trans[3],
                                                    bounds_trans[2]]], 
                                                  colormap=colorfun,
                                                  opacity=0.6, 
                                                  name='Tree Cover Canopy',
                                                  mercator_project=True)

    m.add_child(image_overlay)
    return m


def aggregate_tcc(polygon, tolerance=0.1):
    # 10X speedup for tolerance 0.1
    polygon = polygon.simplify(tolerance)
    
    # crude selection of tcc
    x_min, y_min, x_max, y_max = polygon.bounds
    df_tcc = gpdf.loc[gpdf.latitude.between(y_min, y_max) & 
                      gpdf.longitude.between(x_min, x_max)]
    
    # Aggregate TCC within polygon
    try: 
        tcc_polygon = df_tcc.loc[df_tcc.centroid.within(polygon)]
        return tcc_polygon.tcc.mean()
    # for the 1km resolution (but NOT the 10km resolution), getting TopologyException
    # internet suggests self-intersecting polygons? 
    except: 
        return np.NaN


def scatter_tcc_by_city(df_city: gpd.GeoDataFrame):
    data = df_city

    data['size'] = data['POP2010'] / data['POP2010'].max() * 100

    cities_to_label=['New York', 'Miami', 'Boston', 'Raleigh', 'Nashville', 'San Francisco', 'Atlanta', 
                    'Phoenix', 'Los Angeles', 'Chicago', 'Washington', 'Seattle']
    d = data.loc[~data.NAME.isin(cities_to_label)]
    fig = go.Figure(data=go.Scatter(
        x=d['population_density'],
        y=d['tcc'],
        mode='markers',
        marker=dict(size=d['size'],
                    color=d['tcc'],
                   colorscale='YlGn'),
        text=d['NAME'],
    ))

    d = data.loc[data.NAME.isin(cities_to_label)]
    fig.add_trace(go.Scatter(
        x=d['population_density'],
        y=d['tcc'],
        mode='markers+text',
        marker=dict(size=d['size'],
                    color=d['tcc'],
                   colorscale='YlGn'),
        text=d['NAME'],
        textposition="top center"
    ))


    fig.update_layout(title='Tree Cover Canopy for Major US Cities',
                      xaxis_title='Population Density (people per square mile)  |  Bubble size is population', yaxis_title='Tree Cover Canopy (%)',
                     showlegend=False)
    return fig


def save_tif_files():
    logging.warn('This will take lots of RAM')
    tcc = TreeCanopyCover('data/raw/usfs_2016_CONUS_canopy_analytical_12-14-2018_u8.img', resolution=0.1)
    tcc.save_tif('data/tcc_10km_resolution.tif')
    tcc = TreeCanopyCover('data/raw/usfs_2016_CONUS_canopy_analytical_12-14-2018_u8.img', resolution=0.01)
    tcc.save_tif('data/tcc_1km_resolution.tif')
