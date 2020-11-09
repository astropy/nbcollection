# nbcollection-ci

`nbcollection-ci` is a suite of CLI tools designed to simplify maintaining, converting, and testing collections 
of Jupyter notebooks. The goal is to empower communities using GitHub, CircleCI, Jenkins and similar CI 
tools, to assist with building and reviewing Jupyter notebooks.

## Documentation URL

https://nbcollection.readthedocs.io/en/latest/

## Feature Request List

### Isolated Build Environments

Isolated build environments allow for notebooks to be built and rendered per PR. The build process shall not build
all notebooks in the branch submitted to the PR. Instead, it'll do its best to detect a change in a notebook file and
schedule those notebooks for render

### Replication

The Review process has many steps. Each notebook must be reviewed by atleast three members. To make replication across
all environments easier. We'll implement a command that'll allow us to install a notebook from a Pull Request. Users
can than install this software and quickly install the requirements of a notebook locally and start working

The replicate command will analyze metadata of a PR, or other type of URL, and create an environment locally
```
$ pip install nbcollection
$ nbcollection-ci replicate --environment https://github.com/spacetelescope/dat_pyinthesky/pull/111 --directory /tmp/spacetelescope/dat_pyinthesky/pull/111
```

### Install Build Machinery

Installing and updating build machinery can be a task. We'll like to reduce the level of manual effort by automating
the installation and update of all build machinery Astropy provides.

The `install` command will analyze metadata of a Repository and install build machinery
```
$ pip install nbcollection
$ nbcollection-ci install -t circle-ci -r https://github.com/adrn/nbcollection
```
### Uninstall Build Machinery

### Notebook Testing

Integration tests for each cell execution would be nice. This'll protect against a few different issues. The most
immediate being data issues, incase a URL has changed its response or other issues. I haven't explored what we can do
with this, but we should be able to analyze the cell-output to see if anything has changed

## Planned features:

### nbcollection-ci install

`nbcollection-ci install` provides a complete API to install Github Actions or CircleCI CI/CD build machinery for
both Local Repositories and Github Repositories. There is room to expand the API to include support for GitLab and
Bitbucket. Support for `mercurial` can also be added

```
nbcollection-ci install --ci-type circle-ci --repo-path git@github.com:jbcurtin/nbcollection-notebook-test-repo.git
nbcollection-ci install --ci-type circle-ci --repo-path https://github.com/jbcurtin/nbcollection-notebook-test-repo
nbcollection-ci install --ci-type circle-ci --repo-path /tmp/local-repo

nbcollection-ci install --ci-type guthub-actions --repo-path git@github.com:jbcurtin/nbcollection-notebook-test-repo.git
nbcollection-ci install --ci-type github-actions --repo-path https://github.com/jbcurtin/nbcollection-notebook-test-repo
nbcollection-ci install --ci-type github-actions --repo-path /tmp/local-repo
```

### nbcollection-ci uninstall

`nbcollection-uninstall` provides a complete API to uninstall GithActions or CircleCI CI/CD build machinery. The API
provides

### nbcollection-ci venv


* Completely automat adeploy CI/CD PipelineTypes to Github Actions and CircleCI
* Github Actions, CircleCi for CI/CD


## Testing, Development, and Build for nbcollection-ci

`nbcollection-ci` is being designed to make integration with jupyter-lab seemless. It'll have a complete suite of
commands to build, render, and destribute notebooks in HTML. `nbcollection` is being developed in parallel. 

### Interface design

My goal is to build a CLI interface for `nbcollection-ci` with all characteristics of `nbcollection` CLI interface. The
coding style of `nbcollection-ci` should be a little more relaxed, taking influance from `nbcollection` but not strickly
adhearing to the same style of `nbcollection`. Instead, contributors are expected to follow only Pep-8.

### Scripts and CI/CD

`build.sh` exists to quicken common manual routines. At somepoint it should be ported to python/pytest after a
CI/CD solution is choosen https://github.com/astropy/nbcollection/issues/2

#### ci_requirements.txt

`ci_requirements.txt` contains everything needed to run tests for `nbcollection-ci`

