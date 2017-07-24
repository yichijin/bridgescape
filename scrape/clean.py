#!/usr/bin/python3
'''
clean.py

Last updated: 07/17/17
Author: Jimmy Jin

This file used for cleaning erroneously-scraped linfiles.

Currently the scraping routing is imprecise and will scrape
error HTTP responses from the server into some of the linfiles.
It's infrequent (0.5% of all attempts), but throws off the 
parser so they need to be removed before starting.

All well-formed linfiles begin with the flag 'pn|' so remove
all files without this signal.
'''


import os
import re

walk_dir = '/home/ubuntu/data/bridge/'

count = 0

for (dirpath, dirname, filenames) in os.walk(walk_dir):
    for name in filenames:
        fname = os.path.join(dirpath, name)
        linno = name.split('.')[0]

        rem = False

        with open(fname) as f:
            firstline = f.readline()
            if re.match(r'^pn\|', firstline):
                continue
            else:
                rem = True

        if rem==True:
            os.remove(fname)
            count+=1

print('Removed {} empty linfiles.'.format(count))

