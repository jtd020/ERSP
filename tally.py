import json
import cssutils
import logging
from pprint import pprint
import os
import sys
import operator

sys.setrecursionlimit(30000)
cssutils.log.setLevel(logging.CRITICAL)
with open('state.json') as data_file:
    data = json.load(data_file)

ERROR_KEYS = ["MEDIA_RULE", "UNKNOWN_RULE", "CHARSET_RULE"]
dct = {}
tally = 0
num_files = 0

#Directory Path
path_parent = 'C:\windows10share\\batchtest1reduced'
print (path_parent)

#Tally up a:link selector
for path, dirs, file in os.walk(path_parent):
    if len(file) == 0:
        continue
    num_files += 1
    with open(path + "\\" + file[0]) as data_file:
        data = json.load(data_file)

    for i in range(len(data["css"])):
        if " a:link" in data["css"][i]["src"]:
            tally += 1
            break

    dct = {}

#Tally up a:visited selector
for path, dirs, file in os.walk(path_parent):
    if len(file) == 0:
        continue
    num_files += 1
    with open(path + "\\" + file[0]) as data_file:
        data = json.load(data_file)

    for i in range(len(data["css"])):
        if " a:visited" in data["css"][i]["src"]:
            tally += 1
            break

    dct = {}

tally_link_visited = 0
for path, dirs, file in os.walk(path_parent):
    visited = False
    link = False
    if len(file) == 0:
        continue
    num_files += 1
    with open(path + "\\" + file[0]) as data_file:
        data = json.load(data_file)

    for i in range(len(data["css"])):
        if " a:visited" in data["css"][i]["src"]:
            visited = True
        if " a:link" in data["css"][i]["src"]:
            link = True
        if link and visited:
            tally_link_visited += 1
            break
