# nbpages

Tools for building collections of notebooks into web pages for public consumption. 

There are two versions, outlined below.  They use cookiecutter to build a notebook repository, but depend on shared python code in this package (which depends heavily on [nbconvert](https://nbconvert.readthedocs.io)).  The cookiecutter templates that generate these  repository are in separate branches in *this* repo named ``cookiecutter_*``.

## nbpages-html

This is the simpler version, which uses a set of templates to generate an html site directly from the notebooks.  To set up a repo for this version, do:

``` sh
$ cookiecutter gh:eteq/nbpages --checkout cookiecutter_html
```

Once this has been created, the build step is simply:

``` sh
$ python convert.py
```

Which should generate your html pages.


## nbpages-sphinx

This version uses the same input notebook layout, but instead uses [sphinx](http://www.sphinx-doc.org/en/master/).  That is, it converts the notebooks to RST, then runs sphinx to generate the web page.  While this is more complex (and there is therefore more to go wrong), it allows intermixing of notebook pages and narrative text without needing to hand-write any HTML.  It also provides all the sphinx indexing, code-documenting, and linking goodness for cases where that is desirable.

To set up a repo in this case, do:

``` sh
$ cookiecutter gh:eteq/nbpages --checkout cookiecutter_sphinx
```

but then do the standard build as for a sphinx project:

``` sh
$ make html
```

This should automatically do the notebook to RST conversion as a pre-step.
