#!/bin/bash
sphinx-apidoc -f -o . . genohm/tests/*
make html