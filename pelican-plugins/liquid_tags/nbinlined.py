"""
Example:

 {% nbinlined Introducing_HoloViews.ipynb  48 <img | <img width='50%' %}
"""
import os
import base64
from .mdx_liquid_tags import LiquidTags


import IPython
IPYTHON_VERSION = IPython.version_info[0]


SYNTAX = '{% nbinlined notebook cell_no  [ match | replacement ] %}'

@LiquidTags.register('nbinlined')
def nbinlined(preprocessor, tag, markup):
    try:
        split = markup.split()
        if len(split) == 2:
            (nbname, cell_no) = split
            match = None
        elif len(split) > 2:
            (nbname, cell_no) = split[:2]
            substitution = ' '.join(split[2:])
            if '|' not in substitution:
                ValueError("Use pipe symbol | to split match and replacement strings")
            print substitution
            (match, replacement) = substitution.split('|')
    except:
        raise ValueError('Error processing input. '
                         'Expected syntax: {0}'.format(SYNTAX))

    nb_dir =  preprocessor.configs.getConfig('NOTEBOOK_DIR')
    nb_path = os.path.join('content', nb_dir, nbname)

    if not os.path.exists(nb_path):
        raise ValueError("File {0} could not be found".format(nb_path))

    try:
        cell_no = int(cell_no)
    except:
        raise ValueError("Cell number must be supplied as an integer")

    with open(nb_path) as f:
        nb_text = f.read()

    if IPYTHON_VERSION < 3:
        try:
            nb_json = IPython.nbformat.current.reads_json(nb_text)
        except Exception as e:
            print str(e)
    else:
        nb_json = IPython.nbformat.reads(nb_text, as_version=4)

    try:
        # cell = nb_json['worksheets'][0]['cells'][cell_no]
        cell = nb_json['cells'][cell_no]

    except:
        raise ValueError("Could not grab cell %d" % cell_no)

    if 'outputs' not in cell:
        raise ValueError("Cell %d lacks output" % cell_no)

    html = cell['outputs'][0]['data'].get('text/html', None)
    if html is None:
        raise ValueError("Cell %d lacks HTML output" % cell_no)

    if match is not None:
        html = html.replace(match, replacement)
    return html

# Register
from .liquid_tags import register
register()
