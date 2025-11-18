#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, os


sys.path.append('/opt/services/ag/local/lib/python3.10/site-packages')
import bottle

dirpath = os.path.dirname(os.path.abspath(__file__))
#sys.path.append(dirpath)
sys.path.append(os.path.abspath(os.path.join(dirpath,'..','python')))
os.chdir(dirpath)

import renderer
application = bottle.default_app()
