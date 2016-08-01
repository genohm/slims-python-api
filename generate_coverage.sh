#!/bin/bash
pip install coverage
coverage run -m unittest discover genohm/tests/ 
coverage html --omit="/usr/*,/Library/*,~/.virtualenvs/*"
open htmlcov/index.html
