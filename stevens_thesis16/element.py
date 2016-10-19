import os
import json
import param
import numpy as np

from holoviews import Image, Dimension, HoloMap, Store, Curve, NdOverlay
from holoviews.core.options import  Options
from matplotlib import pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

# Silencing bogus matplotlib warnings
import warnings
warnings.filterwarnings('ignore',
                        message="Unicode equal comparison failed to convert both arguments to Unicode",
                        category=UnicodeWarning)



class SpatioTemporalResponse(Image):
    """
    View object that takes a list of curves to be visualized in the
    style of Figure 2E of the 2009 Neuron paper by Yiu Fai Sit:

    "Complex Dynamics of V1 Population Responses Explained by a Simple
    Gain-Control Model".

    The curves are assumed to regularly sampled spatially, from the
    lower spatial extent value to the upper spatial extent value
    supplied.

    The X-axis of the curves (i.e. the temporal, duration component)
    is also expected to be regularly sampled and identical across all
    curves.
    """
    group = param.String(default="SpatioTemporalResponse")

    spatial_extent = param.NumericTuple((0.25, 2.75), length=2, doc="""
      The spatial separation from the first supplied curve to the last
      supplied curve. The curves in between these extremes are
      expected to have been regularly sampled spatially.""")

    bin_width = param.Number(default=1, doc="""
       The temporal duration in milliseconds per sample""")

    kdims=param.List([Dimension('Duration'), Dimension('Position')])

    vdims=param.List([Dimension('Response')])


    @property
    def ndoverlay(self):
        (num_curves, bin_count) = self.data.shape
        milliseconds = np.arange(bin_count) * self.bin_width
        # Will the labels be in the middle of the bins?
        positions = np.linspace(self.spatial_extent[0], self.spatial_extent[1], num_curves)
        curves = {pos:Curve(zip(milliseconds, self.data[ind,:]))
                  for ind, pos in enumerate(positions)}
        return NdOverlay(curves, kdims=['Bin position'])


    def __init__(self, data, spatial_extent=(-0.25, 2.75), bin_width=1, **params):
        if not isinstance(data, np.ndarray):
            data = self._build_array(data)

        ymin, ymax = spatial_extent
        bounds = (0, ymin, len(data[0,:]) * bin_width, ymax)

        # Obey supplied bounds if top and bottom not defaults
        if params.get('bounds', False):
            (dflt_b, dflt_t) = self.params('spatial_extent').default
            (l,b,r,t) = params['bounds'].lbrt()
            if b!=dflt_b or t==dflt_t:
                bounds = (l,b,r,t)

        filtered = {k:v for k,v in params.items() if k not in ['label', 'bounds', 'bin_width']}
        super(SpatioTemporalResponse, self).__init__(data, bounds=bounds,
                                                     bin_width = bin_width,
                                                     **filtered)

    def _build_array(self, data):
        if len(data) < 2:
            raise Exception("At least two curves must be supplied to"
                            " define a spatialtemporal response view.")
        curve_list = [c.last if isinstance(c, HoloMap) else c for c in data]
        xvals = curve_list[0].dimension_values(curve_list[0].kdims[0].name)
        if not all(np.all(c.dimension_values(c.kdims[0].name)== xvals) for c in curve_list):
            raise Exception("All Curves must share common X sampling")
        return np.vstack([c.dimension_values(c.vdims[0].name) for c in curve_list])


def capture_cmap_rgb(filename='../assets/sit_colorbar_clean.png'):
    from PIL import Image as PImage
    im = PImage.open(filename)
    RGB =np.array(im)[:,:,0:3]
    mean = np.mean(RGB, axis=0)

    cmap = []
    for i in range(mean.shape[0]):
        rgb_norm = mean[i,:] / 255
        (h,s,v) = colorsys.rgb_to_hsv(*rgb_norm)
        cmap.append(colorsys.hsv_to_rgb(h,1,v))
    return cmap

asset_path = os.path.join(os.path.split(os.path.realpath(__file__))[0], 'assets')

def register_sit_cmap(filename=asset_path+'/sit_cmap.json',
                      name='sit_cmap', clip_dist=30):
    if filename.endswith('.json'):
        cmap = json.load(open(filename,'r'))
    elif filename.endswith('.png'):
        cmap = capture_cmap_rgb(filname)

    if clip_dist is not None:
        cmap = ([cmap[0]] * clip_dist)+ cmap[clip_dist:]
        cmap = cmap[:-clip_dist] + ([cmap[-1]]*clip_dist)

    sit_cmap = LinearSegmentedColormap.from_list(name, cmap)
    plt.register_cmap(name, sit_cmap)

    data = np.tile(np.linspace(0,1,256),15).reshape(15,256)
    return Image(data)(plot={'aspect':35}, style={'cmap':name})


try: # Skip registration for Travis testing
    sit_cmap_name='sit_cmap'
    register_sit_cmap(name=sit_cmap_name)
except:
    pass

try:  # Avoid requiring matplotlib on Travis
    from holoviews.plotting.mpl import RasterPlot
    # Setting SpatioTemporalResponse to use RasterPlot

    import matplotlib
    Store.register({SpatioTemporalResponse:RasterPlot}, 'matplotlib')
    Store.register({SpatioTemporalResponse:RasterPlot}, 'bokeh')
    yticker = matplotlib.ticker.LinearLocator(2)
    # For SpatioTemporalResponses
    options = Store.options()
    options.SpatioTemporalResponse = Options('style', interpolation='nearest',
                                             cmap=sit_cmap_name)
    options.SpatioTemporalResponse = Options('plot', aspect=10, yticks=yticker)


except:
    pass
