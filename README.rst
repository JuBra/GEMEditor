|Build Status| |Coverage Status| |PyPI|

==========
GEMEditor
==========

GEMEditor as graphical user interface intended at the easy editing of
genome-scale metabolic models. It has been written in an attempt of being
able to integrate the biological information into a consistent metabolic
model referencing the original data being used for reconstruction. GEMEditor
is built on top of cobrapy which is used for model solving. The escher package
is used for the visualization of solutions.


Installation
============

You can download and install the latest version of GEM Editor from pip.

Installation::

    pip install GEMEditor

Updating GEMEditor::

    pip install GEMEditor --upgrade

Usage
=====

Run::

    python -m GEMEditor.run [options]

Options
=======

``--debug``
  Run in debug mode for detailed logging

``--file``
  Path to model

.. |Build Status| image:: https://travis-ci.org/JuBra/GEMEditor.svg?branch=master
   :target: https://travis-ci.org/JuBra/GEMEditor

.. |Coverage Status| image:: https://codecov.io/gh/JuBra/GEMEditor/branch/master/graphs/badge.svg?branch=master
   :target: https://codecov.io/github/JuBra/GEMEditor

.. |PyPI| image:: https://img.shields.io/pypi/v/GEMEditor.svg
   :target: https://pypi.python.org/pypi/GEMEditor