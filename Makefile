release:
	pip install -U twine
	pip install -U setuptools
	pip install -U pip
	make clean
	python setup.py sdist
	python -m twine upload --verbose dist/*

clean :
	rm -rf dist
	rm -rf build
	rm -rf nbcollection.egg-info
	rm -rf .tox
    
install: clean
	pip uninstall nbcollection
	python setup.py build
	python setup.py install

build-docs:
	pip install sphinx sphinx_rtd_theme pip setuptools sphinxcontrib-spelling -U
	mkdir -p /tmp/docs
	rm -rf /tmp/docs/*
	sphinx-build -b spelling -b html docs/ /tmp/docs
