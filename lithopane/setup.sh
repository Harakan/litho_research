#!/bin/bash
#
# What this does:
# 1) Installs 
# 2) Makes a python virtual environment
# -- then sources the activate to jump into it,
# -- and installs any missing libraries I had

#1)
sudo apt install openscad

#2)
virtualenv venv
source venv/bin/activate
pip install wand
