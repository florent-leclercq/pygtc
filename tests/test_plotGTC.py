import warnings
import numpy as np

#Make sure we always use the same backend for image comparison tests
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.testing.decorators import image_comparison

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

try:
    import scipy.ndimage
    from scipy.stats import norm
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False
    
MPLVER = int(matplotlib.__version__.split('.')[0])
if MPLVER < 2:
    warnings.warn('Several tests are known to fail under matplotlib versions less than 2.0. The plots should still look good!', UserWarning)

import pygtc


#Set up some global variables for testing
def _make_random_chain(ndim=4, Npoints=10000, seed = 0):
    np.random.seed(seed)
    means = np.random.rand(ndim)
    cov = .5 - np.random.rand(ndim**2).reshape((ndim,ndim))
    cov = np.triu(cov)
    cov += cov.T - np.diag(cov.diagonal())
    cov = np.dot(cov,cov)
    samples =  np.random.multivariate_normal(means, cov, Npoints)
    return samples

# Create two sets of sample points with 4 parameters and 10000 points
SAMPLES_1 = 2*_make_random_chain(seed = 1)
SAMPLES_2 = 1+_make_random_chain(seed = 2)
SAMPLES_1[:,3]+=1e8
SAMPLES_2[:,3]+=1e8

#Specify kwargs for savefig. We change two things:

#1: bbox tight ensures that the labels don't get cut off.

#2: Set a dpi that won't suck on retina displays and will look fine on anything
#else too. This is only really an issue for raster graphics. Sane people will
#use a vector format, but testing is faster with raster.

SFKWARGS = {'bbox_inches':'tight',
            'dpi':300}


#If this one fails, something is really wrong with matplotlib
@image_comparison(baseline_images=['img'], extensions=['png'], savefig_kwarg=SFKWARGS)
def test_img():
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(1,1)

#A test for (almost) every keyword argument
@image_comparison(baseline_images=['bare'], extensions=['png'], savefig_kwarg=SFKWARGS)
def test_GTC_bare():
    pygtc.plotGTC(chains=[SAMPLES_1,SAMPLES_2],
                    smoothingKernel = 0)

@image_comparison(baseline_images=['pandas'], extensions=['png'], savefig_kwarg=SFKWARGS)
def test_GTC_pandas():
    namesNoTex = ['param name', 'B_labmda', 'C', 'lambda']

    if HAS_PANDAS:
        samples1_pd = pd.DataFrame(SAMPLES_1, columns=namesNoTex)
        samples2_pd = pd.DataFrame(SAMPLES_2, columns=namesNoTex)

    else:
        warnings.warn("Can't test pandas auto-name without pandas. Skipping test.", UserWarning)
        raise nose.SkipTest

    pygtc.plotGTC(chains=[samples1_pd,samples2_pd],
                    smoothingKernel = 0)

@image_comparison(baseline_images=['paramNames_noTex'], extensions=['png'], savefig_kwarg=SFKWARGS)
def test_GTC_paramNames_noTex():
    namesNoTex = ['param name', 'B_labmda', 'C', 'lambda']
    pygtc.plotGTC(chains=[SAMPLES_1,SAMPLES_2],
                    paramNames = namesNoTex,
                    smoothingKernel = 0)

@image_comparison(baseline_images=['paramNames_withTex'], extensions=['png'], savefig_kwarg=SFKWARGS)
def test_GTC_paramNames_withTex():
    namesWithTex = ['param name', '$B_\mathrm{\lambda}$', '$Q^a$', '$\\lambda$']
    pygtc.plotGTC(chains=[SAMPLES_1,SAMPLES_2],
                    paramNames = namesWithTex,
                    smoothingKernel = 0)

@image_comparison(baseline_images=['chainLabels_noTex'], extensions=['png'], savefig_kwarg=SFKWARGS)
def test_GTC_chainLabels_noTex():
    chainLabelsNoTex = ['data1', 'data 2']
    pygtc.plotGTC(chains=[SAMPLES_1,SAMPLES_2],
                    chainLabels = chainLabelsNoTex,
                    smoothingKernel = 0)

@image_comparison(baseline_images=['chainLabels_withTex'], extensions=['png'], savefig_kwarg=SFKWARGS)
def test_GTC_chainLabels_withTex():
    chainLabelsWithTex = ['data1 $\lambda$', 'data 2']
    pygtc.plotGTC(chains=[SAMPLES_1,SAMPLES_2],
                    chainLabels = chainLabelsWithTex,
                    smoothingKernel = 0)

@image_comparison(baseline_images=['truthLabels_noTex'], extensions=['png'], savefig_kwarg=SFKWARGS)
def test_GTC_truthLabels_noTex():
    truths = ((4, .5, None, .1),
                (None, None, .3, 1))
    truthLabelsNoTex = ('the truth', 'alternative truth')
    pygtc.plotGTC(chains=[SAMPLES_1,SAMPLES_2],
                    truths = truths,
                    truthLabels = truthLabelsNoTex,
                    smoothingKernel = 0)

@image_comparison(baseline_images=['truthLabels_withTex'], extensions=['png'], savefig_kwarg=SFKWARGS)
def test_GTC_truthLabels_withTex():
    truths = ((4, .5, None, .1),
                (None, None, .3, 1))
    truthLabelsWithTex = ('the truth $f_0$', 'alternative truth $\\lambda$')
    pygtc.plotGTC(chains=[SAMPLES_1,SAMPLES_2],
                    truths = truths,
                    truthLabels = truthLabelsWithTex,
                    smoothingKernel = 0)

#TODO: Add a test for truthColors

@image_comparison(baseline_images=['truthLineStyles'], extensions=['png'], savefig_kwarg=SFKWARGS)
def test_GTC_truthLineStyles():
    truthLineStyles = ['-', '-']
    truths = ((4, .5, None, .1),
                (None, None, .3, 1))
    pygtc.plotGTC(chains=[SAMPLES_1,SAMPLES_2],
                    truths = truths,
                    truthLineStyles = truthLineStyles,
                    smoothingKernel = 0)

@image_comparison(baseline_images=['priors'], extensions=['png'], tol=5e-3, savefig_kwarg=SFKWARGS)
def test_GTC_priors():
    if not HAS_SCIPY:
        warnings.warn("Can't test priors without scipy installed. Skipping test.", UserWarning)
        raise nose.SkipTest

    priors = (None, (2, 1), (.5, 2), ())
    pygtc.plotGTC(chains=[SAMPLES_1,SAMPLES_2],
                    priors = priors,
                    smoothingKernel = 0)


#TODO: Think up a good way to test plotName

@image_comparison(baseline_images=['nContourLevels'], extensions=['png'], savefig_kwarg=SFKWARGS)
def test_GTC_nContourLevels():
    pygtc.plotGTC(chains=[SAMPLES_1,SAMPLES_2],
                    nContourLevels = 3,
                    smoothingKernel = 0)

@image_comparison(baseline_images=['sigmaContourLevels'], extensions=['png'], savefig_kwarg=SFKWARGS)
def test_GTC_sigmaContourLevels():
    pygtc.plotGTC(chains=[SAMPLES_1,SAMPLES_2],
                    sigmaContourLevels = True,
                    smoothingKernel = 0)

@image_comparison(baseline_images=['nBins'], extensions=['png'], savefig_kwarg=SFKWARGS)
def test_GTC_nBins():
    pygtc.plotGTC(chains=[SAMPLES_1,SAMPLES_2],
                    nBins = 20,
                    smoothingKernel = 0)

@image_comparison(baseline_images=['smoothingKernel'], extensions=['png'], savefig_kwarg=SFKWARGS)
def test_GTC_smoothingKernel():
    if not HAS_SCIPY:
        warnings.warn("Can't test smoothing without scipy. Skipping test.", UserWarning)
        raise nose.SkipTest

    pygtc.plotGTC(chains=[SAMPLES_1,SAMPLES_2],
                    smoothingKernel = 2)

@image_comparison(baseline_images=['filledPlots'], extensions=['png'], savefig_kwarg=SFKWARGS)
def test_GTC_filledPlots():
    pygtc.plotGTC(chains=[SAMPLES_1,SAMPLES_2],
                    filledPlots = False,
                    smoothingKernel = 0)

@image_comparison(baseline_images=['plotDensity'], extensions=['png'], savefig_kwarg=SFKWARGS)
def test_GTC_plotDensity():
    pygtc.plotGTC(chains=[SAMPLES_1,SAMPLES_2],
                    plotDensity = True,
                    smoothingKernel = 0)

@image_comparison(baseline_images=['figureSize'], extensions=['png'], savefig_kwarg=SFKWARGS)
def test_GTC_figureSize():
    pygtc.plotGTC(chains=[SAMPLES_1,SAMPLES_2],
                    figureSize = 'APJ_page',
                    smoothingKernel = 0)

@image_comparison(baseline_images=['panelSpacing'], extensions=['png'], savefig_kwarg=SFKWARGS)
def test_GTC_panelSpacing():
    pygtc.plotGTC(chains=[SAMPLES_1,SAMPLES_2],
                    panelSpacing = 'loose',
                    smoothingKernel = 0)

#TODO: Add a test for legendMarker

#TODO: Add a test for paramRanges

@image_comparison(baseline_images=['labelRotation'], extensions=['png'], savefig_kwarg=SFKWARGS)
def test_GTC_labelRotation():
    pygtc.plotGTC(chains=[SAMPLES_1,SAMPLES_2],
                    labelRotation = (False, False),
                    smoothingKernel = 0)

@image_comparison(baseline_images=['tickShifts'], extensions=['png'], savefig_kwarg=SFKWARGS)
def test_GTC_tickShifts():
    pygtc.plotGTC(chains=[SAMPLES_1,SAMPLES_2],
                    tickShifts = (0.2, 0.2),
                    smoothingKernel = 0)

@image_comparison(baseline_images=['colorsOrder'], extensions=['png'], savefig_kwarg=SFKWARGS)
def test_GTC_colorsOrder():
    pygtc.plotGTC(chains=[SAMPLES_1,SAMPLES_2],
                    colorsOrder = ['purples', 'yellows'],
                    smoothingKernel = 0)

@image_comparison(baseline_images=['do1dPlots'], extensions=['png'], savefig_kwarg=SFKWARGS)
def test_GTC_do1dPlots():
    pygtc.plotGTC(chains=[SAMPLES_1,SAMPLES_2],
                    do1dPlots = False,
                    smoothingKernel = 0)

@image_comparison(baseline_images=['doOnly1dPlot'], extensions=['png'], savefig_kwarg=SFKWARGS)
def test_GTC_doOnly1dPlot():
    input_chains = [np.array([SAMPLES_1[:,0]]).T, np.array([SAMPLES_2[:,0]]).T]
    pygtc.plotGTC(chains=input_chains,
                    doOnly1dPlot = True,
                    smoothingKernel = 0)

@image_comparison(baseline_images=['mathTextFontSet'], extensions=['png'], savefig_kwarg=SFKWARGS)
def test_GTC_mathTextFontSet():
    namesWithTex = ['param name', '$B_\mathrm{\lambda}$', '$Q^a$', '$\\lambda$']
    pygtc.plotGTC(chains=[SAMPLES_1,SAMPLES_2],
                    paramNames = namesWithTex,
                    mathTextFontSet = None,
                    smoothingKernel = 0)

#TODO: Could add a few more tests to deal with label font customization...

if __name__ == '__main__':
    import nose
    nose.runmodule()
