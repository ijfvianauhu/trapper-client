import os
import sys
sys.path.insert(0, os.path.abspath('../../src'))

project = 'Tapper Client'
copyright = '2025, WildIntel project'
author = 'Iñaki Fernández de Viana y González'

extensions = [
    'sphinx.ext.autodoc',
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    'sphinx_autodoc_typehints',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

html_theme = "sphinx_rtd_theme"

html_theme_options = {
    "navigation_depth": 4,
    "collapse_navigation": False,
    "titles_only": False,
}

autodoc_member_order = "bysource"
autodoc_typehints = "description"

html_static_path = ['_static']

extensions.append('recommonmark')
