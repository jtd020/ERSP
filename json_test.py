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

path_parent = 'C:\windows10share\\batchtest1reduced'
print (path_parent)

for path, dirs, file in os.walk(path_parent):
    if len(file) == 0:
        continue
    num_files += 1
    with open(path + "\\" + file[0]) as data_file:
        data = json.load(data_file)

    for i in range(len(data["css"])):
        if "a:link" in data["css"][i]["src"]:
            tally += 1
            break

    dct = {}


for path, dirs, file in os.walk(path_parent):
    if len(file) == 0:
        continue
    num_files += 1
    with open(path + "\\" + file[0]) as data_file:
        data = json.load(data_file)

    for i in range(len(data["css"])):
        if "a:visited" in data["css"][i]["src"]:
            tally += 1
            break

    dct = {}


dct_test = {}
for path, dirs, file in os.walk(path_parent):
    visited = False
    print (path)
    if len(file) == 0:
        continue

    with open(path + "\\" + file[0]) as data_file:
        data = json.load(data_file)

    f = open("something.txt", "w")
    for i in range(len(data["css"])):
        sheet = cssutils.parseString(data["css"][i]["src"])
        for rule in sheet:
            if rule.typeString != "STYLE_RULE":
                continue
            selector = rule.selectorText
            if " a:visited" in selector:
                print(rule)
                styles = (rule.style.cssText).split(";")
                for definition in styles:
                    attribute = definition.split(":")[0].replace("\n","")
                    if attribute not in dct_test:
                        dct_test[attribute] = 1
                    else:
                        dct_test[attribute] += 1
                visited = True
                break
        if visited == True:
            break

    if visited == True:
        sorted_keys = sorted(dct_test.items(), key=operator.itemgetter(1))
        pprint(sorted_keys)

print (tally)
print (tally/num_files)
# f = open("csstest.css", "w")
# f.write(data["css"][0]["src"])