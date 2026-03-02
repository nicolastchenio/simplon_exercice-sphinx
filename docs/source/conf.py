# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys

# Définir les chemins pour trouver notre code
sys.path.insert(0, os.path.abspath('../..'))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'projet_bdd'
copyright = '2026, nicolas tchenio'
author = 'nicolas tchenio'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx_rtd_theme',
    'sphinx.ext.autodoc', # Pour extraire la doc du code
    'sphinx.ext.napoleon', # Pour supporter les docstrings style Google/NumPy
    'sphinx.ext.mathjax', # Pour latex
    "sphinx.ext.viewcode", # pour afficher code source
    "myst_parser", # pour le markdown
]

templates_path = ['_templates']
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']