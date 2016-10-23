from element import SpatioTemporalResponse
import os

asset_path = os.path.join(os.path.split(os.path.realpath(__file__))[0], 'assets')

def notebooks(path='notebooks', verbose=False):
    """
    Copies the notebooks to the supplied path.
    """

    import os, glob
    from shutil import copytree, ignore_patterns

    candidates = [os.path.join(__path__[0], 'notebooks')]

    for source in candidates:
        if os.path.exists(source):
            copytree(source, path, ignore=ignore_patterns('data','.ipynb_checkpoints','*.pyc','*~'))
            if verbose:
                print("%s copied to %s" % (source, path))
            break
