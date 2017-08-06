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
  Run in debug mode for more detailed logging
