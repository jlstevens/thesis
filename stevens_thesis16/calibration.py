import os
import pickle
from math import exp, log
from collections import OrderedDict

import numpy as np
import param
import imagen

from holoviews import Curve, HoloMap, Element, Spline, GridSpace, Image, Histogram, Points, NdOverlay


def Worgotter_PSTH(onset_ms=400, duration_ms=800, peak=1.0, peak_ms=430,
                   peak_relative=True, spline=True):
    """
    Bezier spline reproduction of Worgotter LGN PSTH.

    If peak is a HoloViews object (e.g a Curve or Holomap), the
    maximum ylim of the object will be used as the peak value.
    """
    peak = peak.ylim[1] if isinstance(peak, (Element, HoloMap)) else peak

    d = ("m 0,0 c 0,0 799.00838, 7.50244 7.50243,-7.5024 22.50727,-635.83062 "
         "33.76092,-635.83062 11.25362,0 18.75609,641.45745 41.26336, "
         "641.45745 22.50727,0 20.6317,-200.6899 50.64137,-200.6899 "
         "30.00971,0 39.0194,60.83052 48.76579,71.27306 26.25849,45.014549, "
         "1222.8955,26.258491 11.2537,9.378044 28.1341,135.043659 "
         "43.139,136.919299 15.0049,1.87558 69.3974,20.63167 88.1535,7.50241")

    onset_dflt, peak_dflt, duration_dflt =  398.12, 431.39, 797.89
    onset_index = 1; offset_index = 15; peak_index = 4

    [head, tail] = d.replace('m','').split('c')
    points = [float(el.strip()) for el in tail.replace(',',' ').split()]
    relative_verts = np.array([[x,y] for (x,y) in zip(points[::2],points[1::2])])
    relative_verts *= 0.50
    # Apply shifts while vertices listed as relative shifts
    onset_shift = (peak_ms - peak_dflt) if peak_relative else (onset_ms - onset_dflt)
    relative_verts[onset_index] += [onset_shift, 0]
    relative_verts[offset_index] += [(duration_ms - duration_dflt), 0]
    # Accumulate to turn into absolute coordinates
    x= np.cumsum(relative_verts[...,0])
    y = -np.cumsum(relative_verts[...,1]) * (1.0/ 635) * peak
    point_array = np.column_stack([x,y])
    if not spline: return point_array
    # Takes a cubic bezier path specification (in absolute coordinates) and
    # returns a Matplolib patch. May be obtain from SVG (e.g. from Inkscape).

    # Processes a list of segments, each of which is a numpy array of shape [N,2]
    xabs = point_array[...,0]; yabs= point_array[...,1]
    # Codes correspond to matplotlib.path.Path.[MOVETO | CURVE3]
    codes = [1] + [3]*(len(xabs)-1)
    verts = [(x,y) for (x,y) in zip(xabs,yabs)]
    return Spline((verts, codes))



class IRDModel(object):
    """
    Implements the Invariant Response Description Model of Albrecht et al.
    """

    # Median parameter values
    means = dict(sigmaA=19.0, sigmaB=761.0, alpha=0.27,
                 n=2.4, c50=38.7, tmax=121.0, tshift=65.3,
                 power=1.80, s50=24.6, rmax = 81.8)
    # Median
    median = dict(sigmaA=13.6, sigmaB=543, alpha=0.23,
                  n=2.2, c50=32.3, tmax=114, tshift=61.2,
                  power=1.18, s50=23.1, rmax=50.9)

    # Spread as the standard deviation
    sd = dict(sigmaA=1.91, sigmaB=76.5, alpha=0.03,
              n=0.18, c50=3.51, tmax=4.53, tshift=3.48,
              power=0.28, s50=3.27, rmax=12.2)

    @classmethod
    def latencyV1(cls, contrast, radius=0,
                  tmax=121.0, tshift=65.3, power=1.80, s50=24.6):
        """
        Inverted Naka-Rushton Eqn from Albrecht et al (Eq A3)
        """
        cpower = contrast**power
        spower = s50**power
        frac = cpower / (cpower + spower)
        return tmax - (tshift * frac)

    @staticmethod
    def latency_LGN(contrast, tshift=25.25, power=2.3, s50=14.5):
        """
        Inverted Naka-Rushton Eqn used for the LGN latency.
        Fit using onset values from Sit as follows:

        import numpy as np
        from scipy.optimize import curve_fit
        xdata = np.array([100,50,25,12.5,9,6]) # contrasts
        ydata = np.array([18,21,25,33,36,44])  # latencies
        popt, _ = curve_fit(IRDModel.latency_LGN, xdata, ydata)
        """
        tmax=44  # Fixed estimate to ease fitting procedure
        cpower = contrast**power
        spower = s50**power
        frac = cpower / (cpower + spower)
        return tmax - (tshift * frac)


    @classmethod
    def Naka_Rushton(cls, contrast, n=2.4, c50=38.7):
        """
        Naka-Rushton Eqn from Albrecht et al (Eq A2)
        """
        return contrast**n / (contrast**n + c50**n)

    @classmethod
    def V1PSTH(cls, t, tauC, alpha=0.27, sigmaA=19.0, sigmaB=761.0):
        """
        Albrecht et al (Eq A1)
        """
        deltaTSq = float((t - tauC)**2)
        sigmaASq = sigmaA**2
        sigmaBSq = sigmaB**2

        if t < tauC:
            return exp(-log(2)*(deltaTSq / sigmaASq))
        else:
            gauss1 = exp(-log(2)*(deltaTSq / sigmaBSq))
            gauss2 = exp(-log(2)*(deltaTSq / sigmaASq))
            return (alpha * gauss1) + ((1 - alpha) * gauss2)

    @classmethod
    def sampleV1PSTH(cls, time, contrast=1.0, radius=0,
                     parameters=None, r0=0, shift=50, tauC_shift=0, tauC_lock=100):
        """
        Albrecht et al (Eq A4). Uses median parameter values unless
        otherwise specified.

        r0 is an additional constant term (default 0, no error estimates)
        shift if and offset to match the data.
        """
        p = parameters if parameters is not None else cls.median # Switched to median
        time = time + shift # Offset to match the data
        if tauC_lock:
            tauC = cls.latencyV1(tauC_lock, radius,
                                 p['tmax'],  p['tshift'], p['power'], p['s50'])
        else:
            tauC = cls.latencyV1(contrast, radius,
                                 p['tmax'],  p['tshift'], p['power'], p['s50'])

        # Optional offset to tauC (PSTH latency)
        tauC = tauC + tauC_shift

        unmodulated = cls.V1PSTH(time, tauC, p['alpha'], p['sigmaA'], p['sigmaB'])
        contrastFactor = cls.Naka_Rushton(contrast, p['n'], p['c50'])
        return p['rmax']*contrastFactor*unmodulated + r0


    @classmethod
    def PSTH_Curve(cls, onset=0, offset=250, timestep=1, normalization=1.0,
                   contrast=1.0, radius=0, tuples=False, parameters=None,
                   shift=0, lag=None, tauC_shifter = None,
                   tauC_lock=100, label='IRD_Model'):
        """
        Generate a PSTH curve from the given onset time to the given
        offset time.

        The normalization argument may be a float (with a default of
        1.0) or False, in which case normalization is disabled.
        """
        times = range(onset, offset+1)[::timestep]

        tauC_shift = 0
        if tauC_shifter:
            tauC_shift = tauC_shifter(radius)

        samples = [cls.sampleV1PSTH(t, contrast=contrast, radius=radius,
                                    parameters=parameters, shift=shift,
                                    tauC_shift = tauC_shift, tauC_lock=tauC_lock)
                   for t in times]
        if normalization:
            samples = [normalization * (act / max(samples)) for act in samples]

        if not lag:
            coords = zip(times, samples)
        else:
            coords = [(t, 0 if t<=lag else s) for (t,s) in zip(times, samples)]

        if tuples: return list(coords)
        return Curve(coords,
                     key_dimensions=['Duration'],
                     value_dimensions = ['Activity'],
                     label=label)



class SyntheticProfiles(param.Parameterized):
    """
    A very fast and crude approximation to the afferent activity
    coming into V1.

    Can be turned into a GridSpace of PSTH curves as follows:

    bounds = (-0.45, -0.45, 0.45, 0.45)
    response = SyntheticProfiles()()
    response.sample((15,15),bounds=bounds).to.curve(['Time'], ['z']).grid(['x','y'])
    """

    pattern = param.ClassSelector(default=imagen.Gaussian(aspect_ratio=1.0),
                                  class_=imagen.PatternGenerator, doc="""
       The pattern generator used to generate the spatial profile.""")

    baseline = param.Number(default=0, doc="""
      A baseline response (as a percentage of the contrast) of
      subthreshold activity added to the response after the onset
      lag.""")

    baseline_mode = param.ObjectSelector(default='local',
                                         objects=['global','local'])

    density = param.Integer(default=30, doc="""
       The spatial sampling density for both the xdensity and ydensity""")

    contrast_multiplier = param.Number(default=0,  doc="""
       Multiplier of the contrast to pass to the IRD model. By default
       (a multiplier of zero) will remove the contrast multiplier, leaving
       only the constrast_offset.""")

    peak_scaling = param.Boolean(default=False, doc="""
       Whether or not the peaks of the output are scaled to match the value
       of the spatial pattern at that particular point.""")

    peak_multiplier = param.Number(default=1.0, doc="""
       The multiplier used to scale the output of the model.""")

    onset = param.Integer(default=0, doc="""
       Parameter of IRD.PSTH_Curve of the same name""")

    offset = param.Integer(default=200, doc="""
       Parameter of IRD.PSTH_Curve of the same name""")

    lag_mode = param.ObjectSelector(default='explicit',
                          objects=['explicit', 'variable', 'constant'], doc="""
       Whether to compute the lag as a function of contrast.""")

    lag = param.Integer(default=0, doc=""" Absolute lag time for
       activity to reach V1, used to adjust the Albrecht model based
       on arguments of causality. Clips early time values to zero
       response.""")

    shift = param.Integer(default=0, doc="""
       Translational shift in the IRD model response.""")

    timestep = param.Integer(default=1, doc="""
       Corresponds to the step parameter of IRD.PSTH_Curve.""")

    parameters = param.Dict(default=IRDModel.means, doc="""
       The parameters passed to the IRD model.""")

    spatial_scale=param.Number(default=1, doc="""
       Spatial multiplier from sheet coordinates to IRD radius""")

    PSTH_Model = param.Parameter(default=IRDModel, doc="""
       The PSTH model to allow subclasses of the IRDModel""")

    tauC_shifter = param.Parameter(default=None, doc="""
       Callable to generate tauC offset as a function of radius.""" )

    value_dimension = param.String(default='Response', doc="""
       Name of the value dimension used in the Image elements""" )

    tauC_lock = param.Integer(default=100, allow_None=True, doc="""
      Lock the contrast input to this value for use with
      peak_scaling. If zero or None, peak_scaling must be False and full
      IRD model used.

      Note, if peak_scaling=True, contrast_multiplier is *not* applied.""" )

    def __init__(self, **params):
        super(SyntheticProfiles, self).__init__(**params)

    def __call__(self, mode=None):
        Model = self.PSTH_Model
        self.pattern.xdensity=self.density
        self.pattern.ydensity=self.density

        activities = []
        image = self.pattern[:]

        (d1, d2) = image.data.shape
        m,n = np.mgrid[0:d1,0:d2]

        if self.tauC_lock and not self.peak_scaling:
            raise Exception("The tauC_lock option must be used with peak_scaling=True")
        if not self.tauC_lock and self.peak_scaling:
            raise Exception("If tauC_lock disabled use peak_scaling=False")

        if self.lag_mode != 'explicit' and self.lag:
            raise Exception("Non-zero explicit lag may only be used "
                            "if lag_mode is set to 'explicit'.")

        for ind1, ind2, val in zip(m.flat,n.flat, image.data.flat):
            contrast = (val * self.contrast_multiplier)

            (x,y) = image.matrixidx2sheet(ind1,ind2)
            # Radius in degrees from center
            radius = self.spatial_scale * ((x**2 + y**2)**0.5)

            if self.lag_mode == 'explicit':
                lag = self.lag
            elif self.lag_mode == 'variable':
                lag = Model.latency_LGN(contrast)
            elif self.lag_mode == 'constant':
                lag = Model.latency_LGN(self.contrast_multiplier)

            if self.tauC_lock:
                contrast = self.tauC_lock

            profile = Model.PSTH_Curve(self.onset,
                                       self.offset,
                                       self.timestep,
                                       normalization=val if self.peak_scaling else None,
                                       shift=self.shift,
                                       parameters=self.parameters,
                                       lag = self.lag,
                                       # Lag must also be applied AFTER scatter.
                                       contrast = contrast,
                                       radius=radius,
                                       tauC_shifter=self.tauC_shifter,
                                       tauC_lock=self.tauC_lock,
                                       tuples=True)
            times, values = zip(*profile)
            times = np.array(times)
            values =  np.array(values)

            if self.baseline:
                if self.baseline_mode == 'global':
                    baseline_factor = self.contrast_multiplier
                else:
                    baseline_factor = values.max()
                mask = ((lag < times) & (times < self.offset))
                values = values + (mask * ((self.baseline/100.0) * baseline_factor))

            # Zero out
            mask = (times < lag)
            values[mask]=0
            activities.append([v*self.peak_multiplier for v in values])

        hmap = HoloMap(key_dimensions=['Time'])
        for ind, t in enumerate(times):
            data = np.zeros((d1,d2))
            values = [act[ind] for act in activities]
            for idx1, idx2, val in zip(m.flat,n.flat, values):
                data[idx1,idx2] = val

            hmap[t] = Image(data, vdims=[self.value_dimension])

        return hmap



def nowak_distribution(path=asset_path+'/nowak-hists/nowak_histograms.pkl',
                       condition='mu_ON', scale=None, hist=True,
                       centering='range', extents=False, group='Nowak'):
    """
    Load the captured Nowak latency distributions as either a
    histogram or points.

    Conditions: 'mu_ON', 'mu_OFF', 'su_ON', 'su_OFF'
    """
    assert centering in [None, 'peak', 'range', 'zero-align']
    peaks = {'mu_ON':75, 'mu_OFF':65, 'su_ON':85, 'su_OFF':115}
    ranges = {'mu_ON':100, 'mu_OFF':130, 'su_ON':100, 'su_OFF':130}
    onsets = {'mu_ON':20, 'mu_OFF':30, 'su_ON':30, 'su_OFF':30}

    offset = 0
    if centering == 'range':
        offset = (ranges[condition]/2.0 + onsets[condition])
    elif centering == 'peak':
        offset = peaks[condition]
    elif centering == 'zero-align':
        offset = onsets[condition]

    data = pickle.load(open(path, 'r'))
    frequencies, edges = data[condition]
    if offset != 0:
        edges = [e-offset for e in edges]

    kwargs = dict(group=group)
    if scale is not None:
        frequencies = [f*scale for f in frequencies]
    if extents:
        bounds=data['mu_bounds' if condition.startswith('mu') else 'su_bounds']
        sc = scale if scale else 1.0
        kwargs['extents'] = bounds[:3] + (bounds[-1]*sc,)
    if hist:
        kwargs['kdims'] = ['Onset latency (ms)']
        return Histogram((frequencies, edges), **kwargs)
    else:
        return Points(zip(edges, frequencies), **kwargs)


asset_path = os.path.join(os.path.split(os.path.realpath(__file__))[0], 'assets')
def sit_spatiotemporal_traces(path=asset_path+'/sit_curves/', contrast=100):
    "Helper function to load the captured Sit curves"
    fname = os.path.join(path, 'c%s.npz' % contrast)
    return [Curve(data) for data in np.load(fname)['data']]


def reynaud_spatiotemporal_traces(path=asset_path+'/reynaud-curves/', contrast=80):
    "Helper function to load the captured Reynauld curves (already interpolated)"
    fname = os.path.join(path, 'c%s.npz' % contrast)
    return [Curve(data) for data in np.load(fname)]


def interpolate(data, distance):
    """
    Given the data array of a Curve, return a linearly interpolated
    array with the given interpolation distance.
    """
    xmax, xmin = data[:,0].max() , data[:,0].min()
    samples = int(xmax-xmin) // distance
    xvals = np.linspace(xmin, xmax, samples)
    yinterp = np.interp(xvals, data[:,0], data[:,1])
    return np.vstack([xvals, yinterp]).T


def sit_traces(filename = asset_path+'/sit-curves/raw_traces_c100.npz', interpolation=1, exclude=[]):
    """
    Helper function to load Sit raw traces (Figure 2A).
    The interpolation argument (if not None) is the *approximate*
    linear interpolation distance (in milliseconds).
    """
    npz = np.load(filename)
    if interpolation:
        data =  {k:(interpolate(npz[k][0], interpolation), npz[k][1]) for k in npz.keys()}
    else:
        data =  {k:npz[k] for k in npz.keys()}
    # Exclude option can be removed once styles after NdOverlay slicing is fixed
    return NdOverlay({float(c):Curve(d)(style={'color':col})
                      for c,(d, col) in data.items() if c not in exclude}, kdims=['Contrast'])
