#!/usr/bin/env python

import re

with open('j.json', 'r') as f:
    data = f.read()
    m = re.search((?<="id\s")(.*)), data)
    print(m.group(0))
