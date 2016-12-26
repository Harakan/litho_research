#!/bin/bash
#
# What this does:
# 1) Makes a virtual environment
# 2) sources the activate to jump into it
# 3) installs any missing libraries I had

virtualenv venv
source venv/bin/activate
pip install wand
