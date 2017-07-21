# bridgescrape

This is a suite of tools to scrape, parse, and analyze bridge hand data from the online bridge community BridgeBase Online (BBO).

Complete data on bridge hands and tournaments is publicly available on BBO, but to date has been provided in a cryptic format (.lin files). This repository builds on the work of http://github.com/OneTrickPony82/Bridge-Tools to provide the tools to convert these files into human-readable, Python classes.

These tools are currently still under development. They consist mainly of three parts:

1) parse: the tools for parsing and analyzing .lin files
2) scrape: the tools for scraping .lin files directly from BBO
3) data: a sample of the scraped data from a single pairs tournament

All three folders will be updated as I get more time to work on it. The current data set is comprised of ~600,000 unique boards which consist of roughly ~30,000 unique deals, totaling about 3GB.

# Parsing: linparse.py and the BridgeHand class

The heart of these tools is the BridgeHand class for representing a complete bridge hand, bids, and plays. The BridgeHand class is comprised of the following attributes:

1) BridgeHand.players: a dict of BBO userids, keyed by position ('E', 'S', 'W', 'N')
2) BridgeHand.hands: a dict of Hand objects comprised of Card objects, keyed by position 
3) BridgeHand.bids: a list of str representing the bid sequence
4) BridgeHand.play: a list of dicts, each of which represents a single trick. The trick dicts are keyed by position with Card values, with one extra entry keyed by 'lead' whose value is a position.
5) BridgeHand.contract: string indicating the winning contract
6) BridgeHand.declarer: string indicating the position of the declarer
7) BridgeHand.doubled: int in {0,1,2} indicating whether the contract was undoubled, doubled, or redoubled
8) BridgeHand.vuln:
9) BridgeHand.made: the number of tricks made by the declaring team
10) BridgeHand.claimed: whether play was ended on one side claiming tricks

# The data

The data is publicly available records from bridge games played online on bridgebase.com, the most popular online site for bridge.

BridgeBase keeps records of their games in a propriety .lin format for which public specifications does not exist. However, bridgebase.com also allows users to view previous bridge hands, bids, and plays through an applet as well, so the format can be reverse-engineered.

[insert linfile example here]

BridgeBase runs a variety of tournaments for users to play in, including ones offering robot (AI) opponents. Our data are comprised of only games from the ACBL Speedball hourly tournaments (individual and pairs).

The .lin files are scraped continuously on an AWS instance. The current count for the full data set is ~600,000 unique deals; a small subset is available in the data/ directory to give users an idea of what to expect and to test the parser.

# The scraping

The code used for scraping BBO is offered here although we ask that users be respectful should they choose to use it. Because the .lin files are exposed using link URL hyperlinks, the script is a simple combination of Requests and BeautifulSoup with throttling so as not to overwhelm the server.

