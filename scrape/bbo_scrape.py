#!/usr/bin/python3

'''
date: 10/07/2016
author: Jimmy Jin

This script was created to scrape the BBO ACBL non-robot tournaments.

It scrapes both:
    -Individual tournaments
    -Speedball tournaments

And saves the .lin files to the datadir defined below.

It can be run continuously, and records timestamps to disk to keep
track of what was the latest tournament retrieved. There is probably
a smarter way of doing this but this works for now.
'''

import requests
import re
import json
import time
import os
import datetime as dt
from bs4 import BeautifulSoup

import config

datadir = '/home/yichijin/Dropbox/Research/bridge/data'

# load the last known timestamp scraped (all times UTC)
with open('timestamp.dat','r') as f:
    raw = json.load(f)
last = dt.datetime.strptime(raw, "%Y-%m-%dT%H:%M:%S")

# log in
s = requests.session()
s.post('http://www.bridgebase.com/myhands/myhands_login.php?t=%2Fmyhands%2Findex.php%3F&offset=0', data=config.login)

# outer loop for when all tournaments have been processed 
while True:

    '''
    update timestamp now to mark latest progress -- scrape
    proceeds from latest tournament to the oldest that we
    haven't scraped
    '''

    with open('timestamp.dat','w') as f:
        now = dt.datetime.utcnow()
        json.dump(now.strftime("%Y-%m-%dT%H:%M:%S"), f)

    # (re)load the tournaments page to see what we need to scrape 
    r = s.get('http://webutil.bridgebase.com/v2/tarchive.php?m=h&h=acbl&d=ACBL&o=acbh&offset=0')
    soup = BeautifulSoup(r.text)

    # the first 'tr' cell is just headers
    tr = soup.find('tr')

    # inner loop for processing unprocessed records
    while True:

        # get the tournament time of the next row
        tr = tr.find_next_sibling('tr')
        td = tr.find_all('td')

        # add year to the raw date so Python knows the right decade...
        current_raw = td[0].string.replace(u'\xa0', u' ').lstrip()
        current_year = dt.datetime.today().year
        current_raw = current_raw + ' ' + str(current_year)
        current = dt.datetime.strptime(current_raw, '%a %b %d %I:%M %p %Y')

        # if we're done scraping all new tournaments, rest
        # otherwise, scrape what we need
        if (current < last):
            time.sleep(720)
            last = now
            break
        else:
            # get the type of the tournament
            type = td[3].get_text()
            link = td[5].a['href']

            # save the tournament ID
            tourn_id = link.rpartition('=')[2][:-1]
            print('Entering tournament #' + tourn_id + '...')

            # request + soupify the boards page
            boards = s.get(link + '&offset=0')
            boards_soup = BeautifulSoup(boards.text)

            board_tr = boards_soup.find_all('tr')
            for row in board_tr:
                if row.td is None:
                    continue
                else:
                    traveller_link = row.td.a['href']

                    # save the tournament ID
                    traveller_id = traveller_link.rpartition('-')[2]
                    print('  Getting boards from traveller #' + traveller_id + '...')

                    # soupify the traveller page
                    traveller = s.get('http://www.bridgebase.com' \
                            + traveller_link + '&offset=0')
                    traveller_soup = BeautifulSoup(traveller.text)

                    # get <a> tags to the lin files
                    lintags = traveller_soup.find_all('a', href=re.compile('fetchlin'))

                    # download the .lin files
                    for link in lintags:
                        # get linfile ID
                        lin = link['href'].split('id=')[1].split('&')[0] + '.lin'

                        # download the file
                        filepath = os.path.join(datadir, type,\
                                tourn_id, traveller_id, lin)
                        os.makedirs(os.path.dirname(filepath), exist_ok=True)

                        linfile = s.get('http://www.bridgebase.com/myhands/' \
                                + link['href'])
                        with open(filepath, 'w') as f:
                            f.write(linfile.text)
                        print('    | ' + lin)

                        # sleep so we don't get throttled
                        time.sleep(5)


