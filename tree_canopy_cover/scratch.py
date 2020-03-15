from bokeh.plotting import figure, save
from bokeh.models import ColumnDataSource

def bokeh_plot_tcc(gpdf, df_city):
    """REALLY UGLY IMPLEMENTATION. Also slower than folium rasterlayers"""
    # https://automating-gis-processes.github.io/CSC18/lessons/L5/interactive-map-bokeh.html

    def getPolyCoords(row, geom, coord_type):
        """Returns the coordinates ('x' or 'y') of edges of a Polygon exterior"""

        # Parse the exterior of the coordinate
        exterior = row[geom].exterior

        if coord_type == 'x':
            # Get the x coordinates of the exterior
            return list( exterior.coords.xy[0] )
        elif coord_type == 'y':
            # Get the y coordinates of the exterior
            return list( exterior.coords.xy[1] )

    # Get the Polygon x and y coordinates
    gpdf['x'] = gpdf.apply(getPolyCoords, geom='geometry', coord_type='x', axis=1)
    gpdf['y'] = gpdf.apply(getPolyCoords, geom='geometry', coord_type='y', axis=1)

    # Make a copy, drop the geometry column and create ColumnDataSource
    g_df = gpdf.drop('geometry', axis=1).copy()
    gsource = ColumnDataSource(g_df)


    # Let's first do some coloring magic that converts the color palet into map numbers (it's okey not to understand)
    from bokeh.palettes import Greens9 as palette
    from bokeh.models import LogColorMapper

    # Create the color mapper
    color_mapper = LogColorMapper(palette=palette)


    # Initialize our figure
    p = figure(title="Travel times with Public transportation to Central Railway station")

    # Plot grid
    p.patches('x', 'y', source=gsource,
            fill_color={'field': 'tcc', 'transform': color_mapper},   # todo - colorfun not workingg
            fill_alpha=1.0, line_color="black", line_width=0.05)

    # https://docs.bokeh.org/en/latest/docs/gallery/image.html
    p = figure(title="Travel times with Public transportation to Central Railway station")
    # must give a vector of image data for image parameter
    # p.image(image=[array], x=0, y=0, dw=10, dh=10, palette=pallette, level="image")
    # TODO - not sure how to get dw/dh in pixels from the lat/long degrees
    p.image(image=[array], x=bounds_trans[0], y=bounds_trans[1], dw=10, dh=10, palette=palette, level="image")

    p.grid.grid_line_width = 0.5

    from bokeh.io import output_notebook, show
    output_notebook()

    # Not sure why I get runtime errors
    try: 
        show(p, notebook_handle=True)
    except RuntimeError: 
        show(p, notebook_handle=True)


class TreeCanopyCover:
    """OUTDATED CODE"""
    def __init__(self, filepath, resolution=None, window=None):

        if window: 
            raise NotImplementedError('windowed read not implemented')
            # TODO - warning - I think this doesn't work
            self.window = window
            # self.transform = windows.transform(self.window,self.src.transform)
            # self.band = self.src.read(1, window=self.window)
        
        if '.tif' in filepath: 
            self.read_tif(filepath)
            self.resolution = self.transform.a
        elif '.img' in filepath:
            assert resolution, 'resolution required to read img file'
            self.resolution = resolution
            self.read_img(filepath)
        else: 
            raise NotImplementedError('format not recognized')

    def read_tif(self, filepath):
        # Open saved (reprojected) TCC data
        self.src = rasterio.open(filepath)
        self.transform = self.src.transform
        self.array = self.src.read(1)
        
    def read_img(self, filepath):
        
        # Open and reproject the raw TCC data
        self.src = rasterio.open(filepath)
        band = self.src.read(1)

        # Calculate desired lat/long transform 
        window = windows.Window(0, 0, self.src.shape[1], self.src.shape[0]) 
        bbox = windows.bounds(window, self.src.transform)
        transform,width,height = warp.calculate_default_transform(self.src.crs, {"init":"epsg:4326"},
                                                                  window.width,window.height,
                                                                  left=bbox[0],bottom=bbox[1],
                                                                  right=bbox[2],top=bbox[3], 
                                                                 resolution=self.resolution)
        # Reproject
        out_array = np.ndarray((1, height, width))
        warp.reproject(band,
                   out_array,src_crs=self.src.crs,dst_crs={"init":"epsg:4326"},
                   src_transform=self.src.transform,
                   dst_transform=transform)
        self.transform  = transform
        self.array = out_array[0]

    def to_tif(self, filepath='tcc.tif'):

        # Define profile 
        profile = self.src.profile
        profile['crs'] = rasterio.crs.CRS({"init":"epsg:4326"})
        profile['transform'] = self.transform
        profile['height'] = self.array.shape[0]
        profile['width'] = self.array.shape[1]

        with rasterio.Env():
            with rasterio.open(filepath, 'w', **profile) as dst:
                dst.write(self.array.astype(rasterio.uint8))

    def to_gpdf(self):
        # TODO - There's gotta be a better way of doing this
        rows, cols = np.indices(self.array.shape)  
        geoms = []
        vals = []
        for col,row in zip(np.ravel(cols), np.ravel(rows)):
            # NOTE - top_left is x,y
            top_left = self.transform * (col,row)
            latitude = top_left[1]
            longitude = top_left[0]

            geoms += [Polygon([top_left, 
                               (top_left[0]+self.resolution, top_left[1]),
                               (top_left[0]+self.resolution, top_left[1]-self.resolution),
                               (top_left[0], top_left[1]-self.resolution)])]
            # NOTE - out_array is index by (row,col) wherease it is transformed by (col,row)
            vals += [self.array[(row, col)]]

        gpdf = gpd.GeoDataFrame(vals, geoms, columns=['tcc'])
        gpdf.index.name = 'geometry'
        gpdf = gpdf.reset_index()
        return gpdf


def save_tcc_as_tif():
    filepath='data/raw/usfs_2016_CONUS_canopy_analytical_12-14-2018_u8.img'
    tcc = TreeCanopyCover(filepath, resolution=0.01)
    tcc.to_tif('tcc.tif')


def define_window(src: rasterio.src, min_long, max_long, max_lat, min_lat):
    """Transform the specified lat/long into the row/col window"""
    # TODO - I think the width and height of the window are switched?
    xs, ys = warp.transform({'init': 'epsg:4326'}, src.crs, [min_long, max_long], [max_lat, min_lat])
    top_left = (xs[0], ys[0]) * ~src.transform
    bottom_right = (xs[1], ys[1]) * ~src.transform
    width = bottom_right[1] - top_left[1] 
    height = bottom_right[0] - top_left[0]
    # HACK - the first *should* be correct, but I had to switch them to get it to work...
    # window = Window(top_left[0], top_left[1], width, height)
    window = Window(top_left[0], top_left[1], height, width)
    # DEBUGGING
    #     x, y = top_left * src.transform 
    #     longs, lats = warp.transform(src.crs, {'init': 'epsg:4326'}, [x], [y])
    #     top_left_latlong = (lats[0], longs[0])
    return window
