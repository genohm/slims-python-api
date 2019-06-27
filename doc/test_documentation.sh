#!/bin/bash
sphinx-apidoc -o . ../src/ 
make html 
open _build/html/index.html    