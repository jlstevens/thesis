Title: Introduction
Slug: index

This website presents my PhD thesis presenting a unified spatiotemporal
model of the mammalian primary visual cortex. The computational model
presented here aims to unify cortical dynamics that act on developmental
timescales with the transient activity dynamics of vision that apply on
much shorter timescales. The latest version of the thesis document may
be downloaded
[here](https://github.com/jlstevens/thesis/raw/master/thesis.pdf).

As this work is designed to serve as a platform for future research, it
is based entirely on open source tools and all code is publicly
available. Furthermore, this website is intended to serve as a
reproducible record of all the work in this thesis with the LaTeX source
code available [here](https://github.com/jlstevens/thesis). In addition,
the Jupyter notebooks used to generate the non-diagramatic figures in
the thesis document may be found HERE and may be viewed online using the
links in the 'Notebooks' section below.

The BibTex record for this thesis is given by:

<pre>
@PhdThesis{stevens_thesis16,
  Title                    = {{Spatiotemporal properties of evoked neural response in the primary visual cortex}},
  Author                   = {Stevens, Jean-Luc R.},
  School                   = {The University of Edinburgh},
  Year                     = {2016}
}
</pre>


# Jupyter Notebooks

The thesis presents four computational models, namely the SIRD, GCAL,
CGCAL and TCAL models. The source code for the SIRD model is available
as part of the [Python
package](https://github.com/jlstevens/thesis/tree/stevens_thesis16) that
supports this thesis. This code relies on the [HoloViews](holoviews.org)
which was developed as part of this thesis as well as the
[matplotlib](matplotlib.org) plotting library.

The remaining models, namely the GCAL, CGCAL and TCAL models are all
made available together with recent versions of the
[Topographica](topographica.org) neural simulator. All these models
(including the SIRD model) are demonstrated in the following [Jupyter
notebooks](http://jupyter.org/) used to generate all the non-diagramatic
figures in the thesis. To run these notebooks, first install the
supporting Python package with:

```bash
pip install https://github.com/jlstevens/thesis/archive/stevens_thesis16.zip
```

Then run the following command to install the notebooks into the current
working directory:

```bash
python -c 'from stevens_thesis16 import notebooks; notebooks()'
```

Lastly, you can run a Topographica enabled Jupyter notebook server
using in the directory containing the notebooks:

```bash
topographica -n
```


You can also view snapshots of these notebooks online:


[<i>Background</i>](background.html) : Notebook containing all the figures used in Chapter 2. <br>
[<i>A reproducible workflow for exploratory research</i>](reproducibility.html) : Notebook containing all the figures used in Chapter 3.
<br>
[<i>Quantifying the dynamics of cortical development</i>](gcal.html) : Notebook containing all the figures used in Chapter 5. <br>
[<i>Unifying developmental and evoked response dynamics</i>](tcal.html) : Notebook containing all the figures used in Chapter 6, linking to supplementary notebooks as necessary <br>


# Publications


<table style="width:100%" align="left">
  <tr align="left">
    <th>
<a href="http://journal.frontiersin.org/article/10.3389/fninf.2013.00044/full"><b>An automated and reproducible workflow for running and analysing neural simulations using Lancet and IPython Notebook</b</a>
</th>
  </tr>
  <tr>
    <td><i>Jean-Luc R. Stevens, Marco Elver and James A. Bednar</i> </td>
  </tr>
</table>
</br>


<pre>
@Article{stevens_fninf13,
  Title                    = {{An automated and reproducible workflow for running and analysing neural simulations using Lancet and IPython Notebook}},
  Author                   = {Jean-Luc Stevens and Marco Elver and James A. Bednar},
  Journal                  = {Frontiers in Neuroinformatics},
  Year                     = {2013},
  Month                    = {December},
  Pages                    = {44},
  Volume                   = {7},
}
</pre>


<table style="width:100%" align="left">
  <tr align="left">
    <th>
<a href="http://jneurosci.org/content/33/40/15747.short"><b>Mechanisms for Stable, Robust, and Adaptive Development of Orientation Maps in the Primary Visual Cortex</b</a>
</th>
  </tr>
  <tr>
    <td><i>Jean-Luc R. Stevens and Judith S. Law and Jan Antolik and James A. Bednar</i> </td>
  </tr>
</table>
</br>


<pre>
@Article{stevens_jn13,
  Title                    = {{Mechanisms for Stable, Robust, and Adaptive Development of Orientation Maps in the Primary Visual Cortex}},
  Author                   = {Jean-Luc R. Stevens and Judith S. Law and Jan
 Antolik and James A. Bednar},
  Journal                  = {Journal of Neuroscience},
  Year                     = {2013},
  Pages                    = {15747--15766},
  Volume                   = {33},
}
</pre>


<table style="width:100%" align="left">
  <tr align="left">
    <th>
<a href="http://conference.scipy.org/proceedings/scipy2015/pdfs/jean-luc_stevens.pdf"><b>HoloViews: Building Complex Visualizations Easily for Reproducible Science</b</a>
</th>
  </tr>
  <tr>
    <td><i>Jean-Luc R. Stevens and Philipp Rudiger and James A. Bednar</i> </td>
  </tr>
</table>
</br>

<pre>
@InProceedings{stevens_scipy15,
  Title                    = {{HoloViews: Building Complex Visualizations Easily for Reproducible Science}},
  Author                   = {Jean-Luc R. Stevens and Philipp Rudiger and James A. Bednar},
  Booktitle                = {Proc. of the 14th Python in Science Conference},
  Year                     = {2015},
}
</pre>
