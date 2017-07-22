#!/usr/bin/python3

'''
bbo_scrape.py

Last updated: 07/20/17
Author: Jimmy Jin

This file used for scraping the BridgeBaseOnline hand records.

Currently only scrapes tha ACBL Individual/Pairs speedball
tournaments. Occurs hourly. This script scrapes the raw .lin
files which are parsed using linparse.py.
'''

import requests
import re
import json
import time
import os
import datetime as dt
from bs4 import BeautifulSoup
from random import randrange

import config

datadir = '/mnt/data/bridge'

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

    # get 'tr' tags + delete the header
    tr = soup.find_all('tr')
    del tr[0]

    # inner loop for processing unprocessed records
    for top_level_row in tr:

        # get the tournament time of the next row
        td = top_level_row.find_all('td')

        # add year to the raw date so Python knows the right decade...
        current_raw = td[0].string.replace(u'\xa0', u' ').lstrip()
        current_year = dt.datetime.today().year
        current_raw = current_raw + ' ' + str(current_year)
        current = dt.datetime.strptime(current_raw, '%a %b %d %I:%M %p %Y')

        # if we're up to date on tournament, rest; otherwise, keep scraping
        if (current < last):
            
            print('Finished scraping tournaments up til {}, resetting last-scraped to {}'.format(last, now))
            
            '''
            Note: this time must be set to at least 1 hour to allow new
            tournaments to appear--otherwise the script gets stuck.
            '''

            time.sleep(3601)
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

            # get the traveller rows + delete the header
            board_tr = boards_soup.find_all('tr')
            del board_tr[0]

            for row in board_tr:
                traveller_link = row.td.a['href']

                # save the tournament ID
                traveller_id = traveller_link.rpartition('-')[2]
                print('  Getting boards from traveller #' + traveller_id + '...\n')
                print('  Current time: {}'.format(str(dt.datetime.now())))

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
                    time.sleep(randrange(4,10))


