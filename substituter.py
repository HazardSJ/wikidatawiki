#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Published by Hazard-SJ (https://www.wikidata.org/wiki/User:Hazard-SJ)
# under the terms of Creative Commons Attribution-ShareAlike 3.0 Unported (CC BY-SA 3.0)
# https://creativecommons.org/licenses/by-sa/3.0/

import pagegenerators
import pywikibot
import re

site = pywikibot.Site('wikidata', 'wikidata')
source = pywikibot.Page(site, 'Template:Subst only')

def gen():
    templates1 = pagegenerators.NamespaceFilterPageGenerator(pagegenerators.ReferringPageGenerator(source, onlyTemplateInclusion=True), [10])
    templates2 = list()
    for pg in templates1:
        page = pg
        if page.title().endswith(ur"/doc") and pywikibot.Page(site, re.sub('/doc', '', page.title())).exists():
            page = pywikibot.Page(site, re.sub('/doc', '', page.title()))
        if not ur"/" in page.title() and page != source:
            templates2.append(page)
            redirects = page.getReferences(redirectsOnly=True)
            for redirect in redirects:
                templates2.append(redirect)
    return sorted(set(templates2))

def main():
    templates = gen()
    for template in templates:
        match = template.title(withNamespace=False)
        tosubst = pagegenerators.ReferringPageGenerator(template, onlyTemplateInclusion=True)
        for page in tosubst:
            text = page.get()
            oldtext = text
            text = re.sub(ur"\{\{(Template:|)%s" % match,u"{{subst:%s" % template.title(withNamespace=False), text,re.I)
            if not oldtext == text:
                try:
                    page.put(text, comment="Robot: Substituting {{[[Template:%s|%s]]}}" % (match, match))
                except:
                    print "Could not edit"
            else:
                print "No changes made"
    return


if __name__ == "__main__":
    try:
        main()
    finally:
        pywikibot.stopme()
