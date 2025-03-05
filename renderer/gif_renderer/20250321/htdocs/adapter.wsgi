#!/usr/bin/env python3
# coding: utf-8

'''
#再起動のためにプロセスをkillする
def application(environ, start_response):
    if environ['mod_wsgi.process_group'] != '': 
        import signal
        os.kill(os.getpid(), signal.SIGINT)
    return ["killed"]
'''

import sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'python'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'python', 'modules'))

dirpath = os.path.dirname(os.path.abspath(__file__))
sys.path.append(dirpath)
os.chdir(dirpath)
import bottle
import server
application = bottle.default_app()
