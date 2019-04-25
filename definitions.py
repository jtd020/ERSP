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

#Determine number of definitions
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
                styles = (rule.style.cssText).split(";")
                for definition in styles:
                    attribute = definition.split(":")[0].replace("\n","")
                    if attribute not in dct_test:
                        dct_test[attribute] = 1
                    else:
                        dct_test[attribute] += 1
                visited = True
                break
        if visited:
            break

    if visited == True:
        sorted_keys = sorted(dct_test.items(), key=operator.itemgetter(1))
        pprint(sorted_keys)
        f.write(sorted_keys)