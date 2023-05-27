# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
#
# SPDX-FileCopyrightText: (c) 2019-2023 Siemens
# SPDX-License-Identifier: MIT

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
current_dir = os.path.dirname(__file__)
target_dir = os.path.abspath(os.path.join(current_dir, "../sw360"))
sys.path.insert(0, target_dir)
target2 = os.path.abspath(os.path.join(current_dir, "../"))
sys.path.insert(0, target2)


# -- Project information -----------------------------------------------------

project = 'Python interface for SW360'
copyright = '2020-2022, Siemens AG'
author = 'Thomas Graf'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = ['sphinx.ext.autodoc', 'sphinx.ext.autosummary']

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'alabaster'
html_theme_options = {
    "github_user": "sw360",
    "github_repo": "sw360python",
    "github_button": True,
    "fixed_sidebar": True,
    "extra_nav_links": {
        "Package on PyPi": "https://pypi.org/project/sw360/",
        "Source on Github": "https://github.com/sw360/sw360python/",
    },
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
# html_static_path = ['_static']
