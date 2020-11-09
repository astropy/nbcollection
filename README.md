# nbcollection

Tools for building collections of Jupyter notebooks into web pages for public
consumption.

This project serves as a thin wrapper around `nbconvert` to enable converting
and executing directories or directory structures full of Jupyter notebooks to
static HTML pages.

## License

`nbcollection` is free software made available under the MIT License. For details
see the LICENSE file.

--------

## Example usage

### Default behavior:

#### Converting a directory structure of specific notebook files

Imagine we have a directory containing Jupyter notebook files and some other
sub-directories that also contain notebook files, such as:

    my_notebooks
    ├── notebook1.ipynb
    └── sub_path1
        ├── notebook2.ipynb
        └── notebook3.ipynb

From the top level, we could use `nbcollection` to execute and convert all of these
notebook files to HTML by running:

    nbcollection convert my_notebooks

With no options specified, this will create a directory within the specified
path, `my_notebooks/_build`, to store the executed notebooks and the converted
HTML pages:

    my_notebooks
    └── _build
        ├── notebook1.ipynb
        ├── notebook1.html
        └── sub_path1
            ├── notebook2.ipynb
            ├── notebook3.ipynb
            ├── notebook2.html
            └── notebook3.html

If you are only interested in executing the notebooks, you can instead use the
`execute` command:

    nbcollection execute my_notebooks

which still creates a new `_build` path but now only contains the executed
notebook files:

    my_notebooks
    └── _build
        ├── notebook1.ipynb
        └── sub_path1
            ├── notebook2.ipynb
            └── notebook3.ipynb


#### Converting a list of specific notebook files

Instead of running on a full directory, it is also possible to convert or
execute single notebook files (but you should probably use `jupyter nbconvert`
directly), or lists of notebook files. For example, to convert a set of specific
notebook files within the above example directory layout:

    nbcollection convert my_notebooks/notebook1.ipynb my_notebooks/sub_path1/notebook2.ipynb

Because these files could in principle be in two completely separate paths, the
build products here will instead be written to the current working directory by
default (but see the command option `--build-path` below to customize). So, the
above command would result in:

    _build
    ├── notebook1.ipynb
    └── sub_path1
        └── notebook2.ipynb


### Command options:

Several options are available to modify the default behavior of the `nbcollection`
commands.

#### Customizing the build path

As outlined above, the default locations for storing the executed notebooks or
converted HTML pages is either in a parallel directory structure contained
within a `_build` directory created at the top-level of the specified path, or
in a `_build` path in the current working directory (if a list of notebook files
are specified). However, the build path can be overridden and specified
explicitly by specifying the `--build-path` command line flag. For example, with
the notebook directory structure illustrated in the above examples, we could
instead specify the build path with:

    nbcollection convert my_notebooks --build-path=/new/path/my_build

With this option specified, the executed notebook files and converted HTML
notebooks would be placed under `/new/path/my_build` instead.


#### Flattening the built file structure

If your notebook files are spread throughout a nested directory structure, you
may want to place all of the converted notebook files in a single path rather
than reproduce the relative path structure of your content. To enable this, use
the `--flatten` boolean flag. For example, if your content has the following
path structure:

    my_notebooks
    ├── notebook1.ipynb
    └── sub_path1
        ├── notebook2.ipynb
        └── notebook3.ipynb

You can convert all of the notebooks to a single build path with:

    nbcollection convert my_notebooks --flatten

This will result in:

    my_notebooks
    └── _build
        ├── notebook1.ipynb
        ├── notebook2.ipynb
        ├── notebook3.ipynb
        ├── notebook1.html
        ├── notebook2.html
        └── notebook3.html

This command also works in conjunction with `--build-path` if you want to, e.g.,
convert a list of individual notebook files and have the build products end up
in the same root path.


#### Specifying a custom template file

`nbconvert` allows specifying custom `jinja2` [template
files](https://nbconvert.readthedocs.io/en/latest/customizing.html) for
exporting notebook files to HTML. We support this through the `--template`
command-line flag, which allows specifying a path to a `jinja2` template file.
For example:

    nbcollection convert my_notebooks --template-file=templates/custom.tpl


#### Only execute the notebooks

Though the primary utility of `nbcollection` is to enable converting a collection of
notebook files to static HTML pages, you can also use the `nbcollection execute`
command to instead only execute a collection of notebooks. This command is used
the same way as `nbcollection convert`, but also enable executing the notebook files
in place as a way to test the notebooks. To execute a collection of notebooks
in-place (i.e., this will not create a `_build` path with the executed
notebooks):

    nbcollection execute my_notebooks --inplace


# nbcollection-ci

`nbcollection-ci` is a suite of CLI tools designed to simplify maintaining, converting, and testing collections 
of Jupyter notebooks. The goal is to empower communities using CircleCI, Github Actions, Jenkins and similar CI 
tools, to assist with building and reviewing Jupyter notebooks.

## Documentation URL

https://nbcollection.readthedocs.io/en/latest/

