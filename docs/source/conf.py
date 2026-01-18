import os
import sys

# Project information
project = "Video Generation Analysis"
copyright = "2025, Tom Mead"
author = "Tom Mead"
release = "0.1.0"

sys.path.insert(0, os.path.abspath("../.."))

# General configuration
extensions = [
    "sphinx.ext.autodoc",  # Automatically document code from docstrings
    "sphinx.ext.autosummary",  # Generate summary tables for modules
    "sphinx.ext.intersphinx",  # Link to documentation of other projects
    "sphinx.ext.napoleon",  # Support for NumPy and Google style docstrings
    "myst_parser",  # Support for Markdown (.md) files
    "sphinx_rtd_theme",  # Theme
    "sphinx_autodoc_typehints",  # Type hinting support
]

autosummary_generate = True
typehints_use_rtype = True
typehints_fully_qualified = True
simplify_optional_unions = True
add_module_names = False
templates_path = ["_templates"]
modindex_common_prefix = ["video_generation_analysis."]

exclude_patterns = ["_build"]

source_suffix = {
    ".rst": "restructuredtext",
}

myst_enable_extensions = ["colon_fence", "strikethrough", "substitution"]

# HTML output options
html_theme = "sphinx_rtd_theme"
pygments_style = "sphinx"
