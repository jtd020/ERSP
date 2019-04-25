import json
import cssutils
import logging
from pprint import pprint
import os
import sys
import operator

sys.setrecursionlimit(30000)
cssutils.log.setLevel(logging.CRITICAL)
# with open('state.json') as data_file:
#     data = json.load(data_file)

ERROR_KEYS = ["MEDIA_RULE", "UNKNOWN_RULE", "CHARSET_RULE"]
dct = {}
tally = 0
num_files = 0

#Directory Path
path_parent = 'C:\windows10share\\batchtest1reduced'
print (path_parent)

#Determine number of definitions
dct_test = {}
disabled_tally = 0
num_files = 0
for path, dirs, file in os.walk(path_parent):
    num_files += 1
    visited = False
    print (path)
    if len(file) == 0:
        continue

    with open(path + "\\" + file[0]) as data_file:
        data = json.load(data_file)

    f = open("something.txt", "w")
    visited = None
    link = None
    visited_flag = False
    link_flag = False
    for i in range(len(data["css"])):
        sheet = cssutils.parseString(data["css"][i]["src"])
        for rule in sheet:
            if rule.typeString != "STYLE_RULE":
                continue
            selector = rule.selectorText
            if " a:link" in selector:
                link = rule
                link_flag = True
            if " a:visited" in selector:
                visited = rule
                visited_flag = True

            if visited_flag and link_flag:
                break

        if visited_flag and link_flag:
            styles_visited = (visited.style.cssText).split(";")
            styles_link = (link.style.cssText).split(";")
            color_visited = ""
            color_link = ""

            for s in styles_visited:
                if "color" in s:
                    color_visited = s

            for s in styles_link:
                if "color" in s:
                    color_link = s

            # color_visited = [s for s in styles_visited if "color" in s]
            # color_link = [s for s in styles_link if "color" in s]
            try:
                attribute_visited = color_visited.split(":")[1].replace("\n", "")
                attribute_link = color_link.split(":")[1].replace("\n", "")
                if attribute_visited == attribute_link:
                    disabled_tally += 1
            except:
                break
            break

print (disabled_tally/num_files)