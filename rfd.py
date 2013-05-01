#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Published by Hazard-SJ (https://www.wikidata.org/wiki/User:Hazard-SJ)
# under the terms of Creative Commons Attribution-ShareAlike 3.0 Unported (CC BY-SA 3.0)
# https://creativecommons.org/licenses/by-sa/3.0/

import pywikibot
import query
import re
import time

site = pywikibot.getSite()

page = pywikibot.Page(site, "Wikidata:Requests for deletions")

archiveheader = u"{{Archive|category=Archived requests for deletion}}"

page.purgeCache()

#  Not yet implemented
monthmessages = ['january', 'february', 'march', 'april', 'may_long', 'june', 'july', 'august', 'september', 'october', 'november', 'december']
months = list()
monthregex = u"("
for monthmessage in monthmessages:
    month = site.mediawiki_message(monthmessage)
    months.append(month)
    monthregex += u"%s|" % month
monthregex += u"\b)"

def main():
    try:
        if page.getSections(minLevel=2) == []:
            print "There are no requests to check."
            return
    except:
        pass
    text        = page.get()
    pageheader  = re.findall(u".*\n= \{\{.*?\}\} =\n.*?\n<!-- .*? -->", text, re.S)[0]
    allrequests = re.findall(u"== *\[\[.*", text, re.S)[0]
    allrequests = re.sub(u"\n==", u"\n\n==", allrequests, re.S)
    allrequests = re.sub(u"\n\n+", u"\n\n", allrequests, re.S)
    allrequests = re.sub(u"\n==", u"\n\n==", allrequests, re.S)
    allrequests = re.sub(u"== *\[\[(?P<header>.*?)\]\] *== *\n", u"== [[\g<header>]] ==\n", allrequests)
    requests = allrequests.split(u"\n\n\n")
    forarchive = list()
    notforarchive = list()
    toarchive = False
    now = time.mktime(time.gmtime())
    timediff = float(1 * 60 * 60)
    for request in requests:
        timestamps = list()
        timestamps = re.findall(u"\d{1,2}:\d{2},\s\d{1,2}\s\D{3,9}\s\d{4}\s\(UTC\)", request, re.S)
        timestamps = sorted([time.mktime(time.strptime(timestamp[:-6], "%H:%M, %d %B %Y")) for timestamp in timestamps])
        ts = timestamps[-1]
        if re.search(u"\{\{((not )?(done|deleted)|didn\'t delete)(\|.*?)?\}\}", request, re.I) and ((now - ts) > timediff):
            forarchive.append(request)
            toarchive = True
        else:
            notforarchive.append(request)
    if toarchive:
        pagetext = pageheader
        for section in notforarchive:
            pagetext += u"\n\n" + section
        archivetitle = page.title() + u"/Archive/" + time.strftime(u'%Y/%m/%d',time.gmtime())
        archive = pywikibot.Page(site, archivetitle)
        if archive.exists():
            archivetext = archive.get()
        else:
            archivetext = archiveheader
        for section in forarchive:
            archivetext += u"\n\n" + section
        archivecount = len(forarchive)
        if archivecount == 1:
            pagesummary = u"Bot: Archiving %i request to [[%s]]" % (archivecount, archive.title())
            archivesummary = u"Bot: Archived %i request from [[%s]]" % (archivecount, page.title())
        else:
            pagesummary = u"Bot: Archiving %i requests to [[%s]]" % (archivecount, archive.title())
            archivesummary = u"Bot: Archived %i requests from [[%s]]" % (archivecount, page.title())
        pageversion = page.getVersionHistory(revCount=1)[0]
        pageversionuser = pageversion[2]
        params = {
            'action': 'query',
            'list': 'users',
            'ususers': pageversionuser,
            'usprop': 'groups'
            }
        pageversionusergroups = query.GetData(params, site)['query']['users'][0]['groups']
        if u"sysop" in pageversionusergroups:
            pagesummary += u" (previous edit at %s by [[User:%s|%s]] (administrator): '%s')" % (pageversion[1], pageversionuser, pageversionuser, pageversion[3])
        else:
            pagesummary += u" (previous edit at %s by [[User:%s|%s]]: '%s')" % (pageversion[1], pageversionuser, pageversionuser, pageversion[3])
        print pagesummary
        page.put(pagetext, comment = pagesummary)
        archive.put(archivetext, comment = archivesummary)
    else:
        print u"There are no archivable requests."

if __name__ == "__main__":
    try:
        main()
    finally:
        pywikibot.stopme()
