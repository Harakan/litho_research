#!/bin/bash

convert tux.png -set colorspace Gray -separate -average grey_tux.png
