<<<<<<< HEAD
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
path_parent = 'C:\windows10share\\batchtest1'
print (path_parent)

#Tally up a:link selector
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

#Tally up a:visited selector
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
                print(rule)
                styles = (rule.style.cssText).split(";")
                for definition in styles:
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
=======
import json
import cssutils
import logging
from pprint import pprint
import os
import sys

sys.setrecursionlimit(3000)
cssutils.log.setLevel(logging.CRITICAL)
with open('state.json') as data_file:
    data = json.load(data_file)

ERROR_KEYS = ["MEDIA_RULE", "UNKNOWN_RULE", "CHARSET_RULE"]
dct = {}
tally = 0
num_files = 0
# for i in range(len(data["css"])):
#     sheet = cssutils.parseString(data["css"][i]["src"])
#     for rule in sheet:
#         if rule.typeString != "STYLE_RULE":
#             continue
#         selector = rule.selectorText
#         styles = rule.style.cssText
#         dct[selector] = styles
#
# for key in dct.keys():
#     if "a:link" in key:
#         tally += 1

path_parent = 'C:\windows10share\\batchtest1reduced'
print (path_parent)

for path, dirs, file in os.walk(path_parent):
    if len(file) == 0:
        continue
    num_files += 1
    print(num_files)
    with open(path + "\\" + file[0]) as data_file:
        data = json.load(data_file)

    for i in range(len(data["css"])):
        if "a:link" in data["css"][i]["src"]:
            tally += 1
            break
        # sheet = cssutils.parseString(data["css"][i]["src"])
    #         # for rule in sheet:
    #         #     if rule.typeString != "STYLE_RULE":
    #         #         continue
    #         #     selector = rule.selectorText
    #         #     styles = rule.style.cssText
    #         #     dct[selector] = styles
    #
    #     # for key in dct.keys():
    #     #     if "a:link" in key:
    #     #         tally += 1

    dct = {}

for path, dirs, file in os.walk(path_parent):
    print (path)
    if len(file) == 0:
        continue

    with open(path + "\\" + file[0]) as data_file:
        data = json.load(data_file)

    dct_test = {}
    f = open("something.txt", "w")
    for i in range(len(data["css"])):
        sheet = cssutils.parseString(data["css"][i]["src"])
        for rule in sheet:
            if rule.typeString != "STYLE_RULE":
                continue
            selector = rule.selectorText
            styles = rule.style.cssText
            dct_test[selector] = styles

    for key in dct_test.keys():
        if "a:link" in key:


print (tally)
print (tally/num_files)
# f = open("csstest.css", "w")
>>>>>>> 53c1eaa2e35d0dd8f34a7044e7e1746c97c7a9ad
# f.write(data["css"][0]["src"])