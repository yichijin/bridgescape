import requests
import re
import json
import time
from datetime import *

import config

with open('timestamp.dat','w') as f:
    zero = datetime.strptime('Fri Jan 01 12:01 AM 2016', '%a %b %d %I:%M %p %Y')
    json.dump(zero.isoformat(), f)

