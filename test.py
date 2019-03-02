#!/usr/bin/env python

import os

to_file = os.open("mot", os.O_APPEND)
context_src = os.read(to_file, os.path.getsize("mot"))
print(context_src)
