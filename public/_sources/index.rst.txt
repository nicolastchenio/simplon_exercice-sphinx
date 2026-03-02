.. projet_bdd documentation master file, created by
   sphinx-quickstart on Mon Mar  2 16:06:42 2026.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

projet_bdd documentation
========================

Add your content using ``reStructuredText`` syntax. See the
`reStructuredText <https://www.sphinx-doc.org/en/master/usage/restructuredtext/index.html>`_
documentation for details.

.. pour inclure le README.md qui sera lu via  myst_parser (qui est dans les extension de config.py)
.. include:: ../../README.md
   :parser: myst_parser.sphinx_

.. toctree::
   :maxdepth: 2
   :caption: Contents:

Documentation du Code
---------------------

.. automodule:: exercice_sql_alchemy
   :members:
   :undoc-members:
   :show-inheritance: