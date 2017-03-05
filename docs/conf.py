# -*- coding: utf-8 -*-

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

extensions = ['docutils_rosetta.parsers.pod']
master_doc = 'index'
html_theme = 'sphinx_rtd_theme'
exclude_patterns = ['_build', 'lib', 'src', 'include']
