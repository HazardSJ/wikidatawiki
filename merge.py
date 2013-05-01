#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Published by Hazard-SJ (https://www.wikidata.org/wiki/User:Hazard-SJ)
# under the terms of Creative Commons Attribution-ShareAlike 3.0 Unported (CC BY-SA 3.0)
# https://creativecommons.org/licenses/by-sa/3.0/

import pywikibot
from query import GetData
import re
import json

site = pywikibot.getSite()
page = pywikibot.Page(site, u"User:Hazard-Bot/merge.js")
separator = u">"

oldtext = page.get()
newtext = u""
lines = oldtext.splitlines()
processed = list()

#raise(Exception(u"Checkpoint reached"))

for line in lines:
    if separator in line:
        items = line.split(separator)
        items[0] = items[0].strip()
        items[1] = items[1].strip()
        if items[0].startswith(u"Q") and items[1].startswith(u"Q"):
            try:
                source = pywikibot.DataPage(int(items[0][1:]))
                target = pywikibot.DataPage(int(items[1][1:]))
                if source.exists() and target.exists():
                    sourcedata = source.get()
                    targetdata = target.get()
                    newdata = dict()
                    #print u"\tDescriptions"
                    for desclang in sourcedata[u"description"]:
                        #print desclang
                        if not desclang in targetdata[u"description"]:
                            if not u"descriptions" in newdata:
                                newdata[u"descriptions"] = dict()
                            newdata[u"descriptions"][desclang] = { u"language": desclang, u"value": sourcedata[u"description"][desclang] }
                    #print u"\tSitelinks"
                    for linkdbname in sourcedata[u"links"]:
                        #print linkdbname
                        if not linkdbname in targetdata[u"links"]:
                            if not u"sitelinks" in newdata:
                                newdata[u"sitelinks"] = dict()
                            newdata[u"sitelinks"][linkdbname] = { u"site": linkdbname, u"title": sourcedata[u"links"][linkdbname] }
                    #print u"\tLabels"
                    for labellang in sourcedata[u"label"]:
                        #print labellang
                        if not labellang in targetdata[u"label"]:
                            if not u"labels" in newdata:
                                newdata[u"labels"] = dict()
                            newdata[u"labels"][labellang] = { u"language": labellang, u"value": sourcedata[u"label"][labellang] }
                    if newdata:
                        print newdata
                        sourceParams = {
                            'action': 'wbeditentity',
                            'id': source.title(),
                            'summary': u'Robot: Merging items per request',
                            'token': site.getToken(),
                            'bot': 1,
                            'data': json.dumps({}),
                            'clear': 1
                        }
                        targetParams = {
                            'action': 'wbeditentity',
                            'id': target.title(),
                            'summary': u'Robot: Merging items per request',
                            'token': site.getToken(),
                            'bot': 1,
                            'data': json.dumps(newdata)
                        }
                        print GetData(sourceParams)
                        print GetData(targetParams)
                        processed.append(line)
            except:
                pass

for line in lines:
    if not line in processed:
        newtext += u"%s\n" %line

if oldtext != newtext:
    page.put(newtext, comment=u"Robot: Removing merged items")

pywikibot.stopme()
