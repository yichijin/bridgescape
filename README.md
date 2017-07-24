# bridgescape

This is a suite of tools to parse, analyze, and scrape bridge hand data from the online bridge community BridgeBase Online (BBO).

Complete data on bridge hands and tournaments is publicly available on BBO, but to date has been provided in a cryptic format (.lin files). This repository builds on the work of http://github.com/OneTrickPony82/Bridge-Tools to provide the tools to convert these files into human-readable, Python classes.

These tools are currently still under development. The main two modules are:

1) module **bridgescape.linparse**: class definitions for Card, Hand, and BridgeHand and tools for parsing .lin files into BridgeHand objects

2) module **bridgescape.analyze**: tools for analyzing BridgeHands once they have been parsed from the .lin files

In addition, I have also provided supplementary files under two subdirectories:

3) **data/**: a sample of the scraped data from a single pairs tournament

4) **analyze/**: tools for scraping .lin files directly from BBO

All folders will be updated as I get more time to work on the project. The current data set is comprised of ~650,000 unique boards which consist of roughly ~30,000 unique deals, totaling about 3GB.

# Parsing: bridgescape.linparse

The heart of these tools is the BridgeHand class for representing a complete bridge hand, bids, and plays. The BridgeHand class is comprised of the following attributes:

1) **.players**: a dict of BBO userids, keyed by position ('E', 'S', 'W', 'N')
2) **.dealer**: string indicating position of the dealer
3) **.hands**: a dict of Hand objects comprised of Card objects, keyed by position 
4) **.bids**: a list of str representing the bid sequence
5) **.play**: a list of dicts, each of which represents a single trick. The trick dicts are keyed by position with Card values, with one extra entry keyed by 'lead' whose value is a position.
6) **.contract**: string indicating the winning contract
7) **.declarer**: string indicating the position of the declarer
8) **.doubled**: int in {0,1,2} indicating whether the contract was undoubled, doubled, or redoubled
9) **.vuln**: str either 'NS', 'EW', 'both', or 'none'
10) **.made**: the number of tricks made by the declaring team
11) **.claimed**: whether play was ended on one side claiming tricks

The Card and Hand objects have been equipped with simple utility methods to facilitate later analysis. These and other utility routines will be documented as time permits.

# Analysis: bridgescape.analyze

The BridgeHand class has been designed for easy analysis of points, bidding, and play. Currently, only a high card points counter is implemented.

# The data: data/

The data is publicly available records from bridge games played online on bridgebase.com, the most popular online site for bridge.

BridgeBase keeps records of their games in a propriety .lin format for which public specifications does not exist. However, bridgebase.com also allows users to view previous bridge hands, bids, and plays through an applet as well, so the format can be reverse-engineered.

An example .lin file:

```pn|queen3233,buchananj,midmow,gbd5981|st||md|3S345H567QD37TC456,S67H39TD289JC2TQA,S2TJAHJAD46QAC3JK,|rh||ah|Board 1|sv|o|mb|1D|mb|p|mb|p|mb|p|pg||pc|SK|pc|S3|pc|S6|pc|SA|pg||pc|DA|pc|D5|pc|D3|pc|D2|pg||pc|ST|pc|SQ|pc|S4|pc|S7|pg||pc|S8|pc|S5|pc|D8|pc|SJ|pg||pc|HT|pc|HA|pc|H2|pc|H5|pg||pc|HJ|pc|HK|pc|H6|pc|H3|pg||pc|C7|pc|C4|pc|CA|pc|C3|pg||pc|C2|pc|CK|pc|C8|pc|C5|pg||pc|CJ|pc|C9|pc|C6|pc|CQ|pg||pc|H9|pc|S2|pc|H4|pc|HQ|pg||pc|H7|pc|D9|pc|DQ|pc|H8|pg||pc|D4|pc|DK|pc|D7|pc|DJ|pg||pc|S9|pc|DT|pc|CT|pc|D6|pg||```

BridgeBase runs a variety of tournaments for users to play in, including ones offering robot (AI) opponents. Our data are comprised of only games from the ACBL Speedball hourly tournaments (individual and pairs).

Some .lin files are incomplete--meaning play is not completed but there is no indicator of how many tricks were claimed. These files have been removed so that we only have files for which we can completely recover the bid sequence and outcome.

The .lin files are scraped continuously on an AWS instance. The current count for the full data set is ~650,000 unique deals; a small subset is available in the data/ directory to give users an idea of what to expect and to test the parser.

# The scraping: scrape/

The code used for scraping BBO is offered here although we ask that users be respectful should they choose to use it. Because the .lin files are exposed using link URL hyperlinks, the script is a simple combination of Requests and BeautifulSoup with throttling so as not to overwhelm the server.

