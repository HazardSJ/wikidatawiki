#!/usr/bin/python
# -*- coding: utf-8 -*-

import wikipedia as pywikibot
import pagegenerators
import query
import re
import urllib2
import time # Test


wd = pywikibot.getSite('wikidata', 'wikidata')

def getLanguages():
    pwblangs = pywikibot.getSite('en', 'wikipedia').family.languages_by_size

    wddblistparams = {
        'action' : 'paraminfo',
        'modules': 'wbsetsitelink'
        }
    wddblist = query.GetData(wddblistparams, wd)['paraminfo']['modules'][0]['parameters'][7]['type']
    wdlangs = list()
    for wddb in wddblist:
        wdlang = re.sub('(?P<lang>=*)wiki$', '\g<lang>', wddb).replace('_', '-')
        wdlangs.append(wdlang)

    nocdblistsurls = {
        'large' : 'https://noc.wikimedia.org/conf/large.dblist',
        'medium': 'https://noc.wikimedia.org/conf/medium.dblist',
        'small' : 'https://noc.wikimedia.org/conf/small.dblist'
        }
    noclangs = {
        'large': list(),
        'medium': list(),
        'small': list()
        }
    for size in nocdblistsurls:
        for nocdb in urllib2.urlopen(nocdblistsurls[size]):
            if nocdb.endswith('wiki\n'):
                noclangs[size].append(re.sub('(?P<lang>=*)wiki$', '\g<lang>', nocdb).replace('\n', ''))

    languages = {
        'large' : list(),
        'medium': list(),
        'small' : list()
        }
    for size in noclangs:
        for noclang in noclangs[size]:
            if (noclang in pwblangs) and (noclang in wdlangs):
                languages[size].append(noclang)
    return languages


def generatePages(size, site):
    if size == 'large':
        number = 200
    elif size == 'medium':
        number = 100
    elif size == 'small':
        number = 50
    else:
        number = 25

    namespaces = [0, 4, 14]
    
    return pagegenerators.NamespaceFilterPageGenerator(pagegenerators.LogpagesPageGenerator(number = number, mode = 'delete', site = site), namespaces)


def appendText(title, text, summary):
    params = {
	'action': 'edit',
	'title': title,
	'appendtext': text,
	'token': wd.getToken(),
	'summary': summary,
	'bot': 1,
        'notminor': 1
	}
    try:
        result = query.GetData(params, wd)
    except:
        pass
    finally:
        return result

    
def requestDeletion(items):
    if len(items) > 1:
        group = u''
        for item in items:
            try:
                group += u' | %s' % item
            except UnicodeEncodeError:
                pass
        text = u'\n\n== Bulk deletion request: Items for non-notable entities ==\n{{subst:Rfd group%s | reason = No longer meets the [[Wikidata:Notability|notability guideline]] | comment = These items no longer meet the [[Wikidata:Notability|notability guideline]]. }}' % group
        summary = u'Bot: Listing multiple items for deletion'
    else:
        item = items[0]
        text = u'\n\n{{subst:Request for deletion|%s|This item no longer meets the [[Wikidata:Notability|notability guideline]].}}' % item
        summary = u'Bot: Listing [[%s]] for deletion' % item
    appendText('Wikidata:Requests for deletions', text, summary)


def main():
    start = time.strftime(u'%H:%M, %d %B %Y (UTC)', time.gmtime()) # Test
    languages = getLanguages()
    print languages

    rfd = list()

    # Test
    rfdcount = 0
    count = 0
    langs = list()

    for size in languages:
        print '\n\n\nProcessing all %s wikis' % size

        for language in languages[size]:
            print '\n\nProcessing for %s' % languages

            wp = pywikibot.getSite(language, 'wikipedia')

            language2 = language.replace('-', '_') # For Wikibase, which uses based on dbname rather than subdomain

            gen = generatePages(size, wp)

            try:
                for page in gen:
                    try:
                        print u'\n%s' % page
                    except UnicodeEncodeError:
                        print u'\n'

                    if page.exists():
                        print u'Skipping: Page exists in client'
                        continue

                    try:
                        entity = pywikibot.DataPage(page)
                    except:
                        print u'Skipping: Error searching for entity'
                        continue

                    try:
                        data = entity.get()
                    except UnboundLocalError:
                        print u'Skipping: No item in repository'
                        continue
                    except KeyError:
                        print u'Skipping: Strange key error'
                        continue

                    entity.setitem(summary=u"Bot: Removed sitelink for a deleted page", items={'type': u'sitelink', 'site': language2, 'title': ''})

                    # Test
                    count += 1
                    if not language in langs:
                        langs.append(language)

                    if len(data['links']) == 1:
                        item = data['entity'].upper()
                        rfd.append(item)
                        rfdcount += 1 # Test
                    if len(rfd) == 90:
                        requestDeletion()
                        rfd = list()
            except:
                print u'Skipping: Error in generator'
    if rfd:
        requestDeletion(rfd)

    end = time.strftime(u'%H:%M, %d %B %Y (UTC)', time.gmtime()) # Test

    # Test
    stats = """\
* Start: %s
* End: %s
* Edits: %s
* Requested for deletion: %s
* Languages for which edits were made: %s
""" % (start, end, count, rfdcount, langs)
    appendText('Wikidata:Sandbox', '\n\n== Execution statistics ==\n%s' % stats, 'Bot: Leaving execution statistics for owner\'s review')



if __name__ == "__main__":
    try:
        main()
    finally:
        pywikibot.stopme()
