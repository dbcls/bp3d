#!/bin/sh

cd "$(dirname "$0")"
/usr/local/Python2.7/bin/python build.py --include common --include extras --output ../../build/three.js
/usr/local/Python2.7/bin/python build.py --include common --include extras --minify --output ../../build/three.min.js
