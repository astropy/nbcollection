import setuptools

with open('nbpages/version.py') as f:
    exec(f.read())  # creates "version_str"


with open('README.md', 'r') as f:
    long_description = f.read()

setuptools.setup(
    name='nbpages',
    version=version_str,
    author='Erik Tollerud',
    author_email='erik.tollerud@gmail.com',
    description='Tools for building collections of notebooks into web pages for public consumption',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/eteq/nbpages',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research'
    ],
)
