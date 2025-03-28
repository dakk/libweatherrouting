# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
import os
import sys

sys.path.append(os.path.abspath(os.path.join("..", "..")))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
project = "weatherrouting"
copyright = "2017-2025, Davide Gessa (dakk)"
author = "Davide Gessa (dakk)"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.coverage",
    "sphinx.ext.napoleon",
    "sphinx_rtd_dark_mode",
    "sphinx_rtd_theme",
    "myst_nb",
]

templates_path = ["_templates"]
exclude_patterns = []
autodoc_source_dir = [
    "../weatherrouting",
]
pygments_style = "lightbulb"
default_dark_mode = False

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]


# autosummary_imported_members = True
autosummary_generate = True
