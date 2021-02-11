Deploying a website using Github Pages
======================================

With `nbcollection-ci` installed into a CI/CD workflow. Additional options become available, such as deploying a themed
website to Github Pages. Later versions of this documentation will include enabling search functionality and
downloading notebooks from Github Pages.


Generating a Themed Website
+++++++++++++++++++++++++++

`nbcollection-doc-demo` ships with the ability to merge artifacts from CirceCI and a file-system. This is required,
because some notebooks take either a large amount of data or more than available CPUs & Memory available in CircleCI.
The command to merge the two sets of artifacts is the same, as `nbcollection-ci` is intelligent enough to manage and
negotiate a resolution for the merge.

It probably goes without saying, if auto-deployment is enabled in the CircelCI CI/CD workflow. Artifacts built locally
will not be built again and deployed in an automated workflow in the cloud.

Using `nbcollection-doc-demo` as the example. Let's build some notebooks on the file-system. We'll then generate a themed
website from these notebooks.


.. code-block:: bash

    $ git clone git@github.com:jbcurtin/nbcollection-doc-demo.git
    $ cd nbcollection-doc-demo
    $ pip install git+https://github.com/jbcurtin/nbcollection.git
    $ pip install GitPython requests toml PyYaml bs4 jinja2 nbformat nbconvert lxml
    $ nbcollection-ci build-notebooks --collection-names notebooks --category-names asdf_example --project-path $PWD
    $ nbcollection-ci merge-artifacts -o jbcurtin -r nbcollection-doc-demo --collection-names notebooks --ci-mode local


A new website will be generated and distributed into $PWD/site. Any static-site webserver is capable of serving the
content.
