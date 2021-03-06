#! /usr/bin/python2.7
# -*- coding: utf-8 -*-

import os
import urllib2
import html5lib

def get_webpage(f):
    page = html5lib.HTMLParser(\
        tree=html5lib.treebuilders.getTreeBuilder("lxml"),\
        namespaceHTMLElements=False)
    p = page.parse(f)
    return p

def get_elements(p, x):
    elems = p.xpath(x)
    e = [list(elem.itertext()) for elem in elems]
    return e

def get_committee_code(inf, x):
    with open(inf, 'r') as f:
        p = get_webpage(f)
        e = p.xpath(x)[0:]

    codes = [i[i.index('(')+1:i.index(')')] for i in e]

    return codes

def get_committee_name(inf, x):
    with open(inf, 'r') as f:
        p = get_webpage(f)
        e = p.xpath(x)[0:]

    return e

def get_committee_list(inf, x):
    with open(inf, 'r') as f:
        p = get_webpage(f)
        e = get_elements(p, x)

    return ['"%s","%s","%s","%s","%s"' % (i[1].strip(), i[3].strip(), i[5].strip(), i[7].strip(), i[10].strip()) for i in e[1:]]

def crawl(url, directory, filename):
    r = urllib2.urlopen(url)
    with open('%s/%s.html' % (directory, filename), 'w') as f:
        f.write(r.read())
    print '%s to %s/%s.html' % (filename, directory, filename)

def parse(directory, filename, rng=None):
    url = 'http://www.assembly.go.kr/assm/assmCommittee/committeePopupAddrView.do?dept_cd=%s'
    x = '//a[contains(@onclick, "jsDeptAddrPopup")]/@onclick'
    x_name = '//h4[@class="title02"]/node()'
    x2 = '//table/*/tr'

    inf = '%s/1.html' % directory
    committee_codes = get_committee_code(inf, x)
    committee_names = get_committee_name(inf, x_name)

    for p in committee_codes:
        crawl(url % p, directory, p)

    index = 0

    with open(filename, 'wa') as merged:
        merged.write('"committe","title","political party","name","phone","email"\n')

        for p in committee_codes:
            n = ('%s' % filename).replace(".csv",'_%s.csv' % committee_names[index])
            with open(n, 'wa') as f:
                inf = '%s/%s.html' % (directory, p)
                committee_list = get_committee_list(inf, x2)

                merged.write((('"%s",') % committee_names[index]).encode('utf-8'))
                merged.write((('\n"%s",') % committee_names[index]).join(committee_list).encode('utf-8'))
                merged.write('\n')

                f.write('"title","political party","name","phone","email"\n')
                f.write('\n'.join(committee_list).encode('utf-8'))
                f.write('\n')
                print 'parsed %s' % inf

            index = index + 1

        merged.write('\n')
        print 'Result written to ' + filename
