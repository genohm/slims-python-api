#!/bin/bash
sphinx-apidoc -f -o . ../src/ 
make html 
open _build/html/index.html    