# -- coding: latin-1
""" pageparser.py - Module to parse an html page and
    extract its links. This module is part of the
    HarvestMan program.

    Author: Anand B Pillai <anand at harvestmanontheweb.com>
    
    For licensing information see the file LICENSE.txt that
    is included in this distribution.

    Modification History
    ====================


   Jan 2007       Anand              Complete support for META robot tags implemented.
                                     Requested by jim sloan of MCHS.
   Mar 06 2007    Anand              Added support for HTML EMBED & OBJECT tags.
   Apr 18 2007    Anand              Made to use the urltypes module.
   Apr 19 2007    Anand              Created class HarvestManCSSParser to take
                                     care of parsing stylesheet content to extract
                                     URLs.
   Aug 28 2007    Anand              Added a parser baed on Effbot's sgmlop
                                     to parse pages with errors - as a part of
                                     fixes for #491.
   Sep 05 2007    Anand              Added a basic javascript parser to parse
                                     Javascript statements - currently this can
                                     perform Javascript based site redirection.
   Sep 10 2007    Anand              Added logic to filter junk links produced
                                     by web-directory pages.
   Oct 3  2007    Anand              Removed class HarvestManJSParser since its
                                     functionality and additional DOM processing
                                     is done by the new JSParser class.
   
  Copyright (C) 2004 Anand B Pillai.                                     
                                     
"""

__version__ = '2.0 b1'
__author__ = 'Anand B Pillai'

from sgmllib import SGMLParser
from urltypes import *
from common.common import *

import re

class HarvestManSimpleParser(SGMLParser):
    """ An HTML/XHTML parser derived from SGMLParser """

    query_re = re.compile(r'[-.:_a-zA-Z0-9]*\?[-.:_a-zA-Z0-9]*=[-.a:_-zA-Z0-9]*')
    skip_re = re.compile(r'(javascript:)|(mailto:)|(news:)')
    # Junk URLs obtained by parsing HTML of web-directory pages
    # i.e pages with title "Index of...". The filtering is done after
    # looking at the title of the page.
    index_page_re = re.compile(r'(\?[a-zA-Z0-9]=[a-zA-Z0-9])')
    
    handled = { 'a' : (('href', TYPE_ANY), ('href', TYPE_ANCHOR)),
                'base': (('href', TYPE_BASE),),
                'frame': (('src', TYPE_FRAME),),
                'img' : (('src', TYPE_IMAGE),),
                'form' : (('action', TYPE_FORM),),
                'link' : (('href', TYPE_ANY),),
                'body' : (('background', TYPE_IMAGE),),
                'script' : (('src', TYPE_JAVASCRIPT),),
                'applet' : (('codebase', TYPE_JAPPLET_CODEBASE), ('code', TYPE_JAPPLET)),
                'area' : (('href', TYPE_ANY),),
                'meta' : (('CONTENT',TYPE_ANY),('content', TYPE_ANY)),
                'embed': (('src', TYPE_ANY),),
                'object': (('data', TYPE_ANY),)
                }

    # Valid 'rel' values - Added Jan 10 06 -Anand
    handled_rel_types = ( TYPE_STYLESHEET, )
    
    def __init__(self):
        self.links = []
        self.linkpos = {}
        self.images = []
        # Fix for <base href="..."> links
        self.base_href = False
        # Base url for above
        self.base = None
        # anchor links flag
        self._anchors = True
        # For META robots tag
        self.can_index = True
        self.can_follow = True
        # Current tag
        self._tag = ''
        # Page title
        self._pagetitle = ''
        SGMLParser.__init__(self)
        
    def save_anchors(self, value):
        """ Set the save anchor links flag """

        # Warning: If you set this to true, anchor links on
        # webpages will be saved as separate files.
        self._anchors = value

    def filter_link(self, link):
        """ Function to filter links, we decide here whether
        to handle certain kinds of links """

        if not link: return

        # ignore javascript links (From 1.2 version javascript
        # links of the form .js are fetched, but we still ignore
        # the actual javascript actions since there is no
        # javascript engine.)
        llink = link.lower()

        # Skip javascript, mailto, news and directory special tags.
        if self.skip_re.match(llink):
            return 1

        # If this is a web-directory Index page, then check for
        # match with junk URLs of such index pages
        if self._pagetitle.lower().startswith('index of'):
            if self.index_page_re.match(llink):
                # print 'Filtering link',llink
                return 1
            
        cfg = GetObject('config')

        # Check if we're accepting query style URLs
        if not cfg.getquerylinks and self.query_re.search(llink):
            return 1

        return 0

    def handle_anchor_links(self, link):
        """ Handle links of the form html#..."""

        # if anchor tag, then get rid of anchor #...
        # and only add the webpage link
        if not link: return

        # Need to do this here also
        self.check_add_link(TYPE_ANCHOR, link)

        # No point in getting #anchor sort of links
        # since they point to anchors in the same page

        # Jan 4 06: Fixed a bug here - This routine
        # was adding a lot of duplicate links. Made
        # it to call check_add_link instead of
        # adding directly.
        
        index = link.rfind('.html#')
        if index != -1:
            newhref = link[:(index + 5)]
            self.check_add_link(TYPE_WEBPAGE, newhref)
            return 0
        else:
            index = link.rfind('.htm#')
            if index != -1:
                newhref = link[:(index + 4)]
                self.check_add_link(TYPE_WEBPAGE, newhref)
            return 0

        return 1

    def unknown_starttag(self, tag, attrs):
        """ This method gives you the tag in the html
        page along with its attributes as a list of
        tuples """

        # Set as current tag
        self._tag = tag
        # print self._tag, attrs
        
        if not attrs: return
        isBaseTag = not self.base and tag == 'base'
        
        if tag in self.handled:

            d = CaselessDict(attrs)
            
            _values = (self.handled[tag])

            link = ''

            for v in _values:
                key = v[0]
                typ = v[1]

                # If there is a <base href="..."> tag
                # set self.base_href
                if isBaseTag and key=='href':
                    self.base_href = True
                    try:
                        self.base = d[key]
                    except:
                        self.base_href = False
                        continue
                
                # if the link already has a value, skip
                # (except for applet tags)
                if tag != 'applet':
                    if link: continue

                if tag == 'link':
                    try:
                        # Fix - only reset typ if it is one
                        # of the valid handled rel types.
                        foundtyp = d['rel'].lower()
                        if foundtyp in self.handled_rel_types:
                            typ = getTypeClass(foundtyp)
                    except KeyError:
                        pass

                try:
                    if tag == 'meta':

                        # Handle meta tag for refresh
                        foundtyp = d.get('http-equiv','').lower()
                        if foundtyp.lower() == 'refresh':
                            link = d.get(key,'')
                            if not link: continue
                            # This will be of the form of either
                            # a time-gap (CONTENT="600") or a time-gap
                            # with a URL (CONTENT="0; URL=<url>")
                            items = link.split(';')
                            if len(items)==1:
                                # Only a time-gap, skip it
                                continue
                            elif len(items)==2:
                                # Second one should be a URL
                                reqd = items[1]
                                if (reqd.find('URL') != -1 or reqd.find('url') != -1) and reqd.find('=') != -1:
                                    link = reqd.split('=')[1].strip()
                                else:
                                    continue
                        else:
                            # Handle robots meta tag
                            name = d.get('name','').lower()
                            if name=='robots':
                                robots = d.get('content','').lower()
                                # Split to ','
                                contents = [item.strip() for item in robots.split(',')]
                                # Check for nofollow
                                self.can_follow = not ('nofollow' in contents)
                                # Check for noindex
                                self.can_index = not ('noindex' in contents)
                            else:
                                continue

                    elif tag != 'applet':
                        link = d[key]
                    else:
                        link += d[key]
                        if key == 'codebase':
                            if link:
                                if link[-1] != '/':
                                    link += '/'
                            continue                                
                except KeyError:
                    continue

                # see if this link is to be filtered
                if self.filter_link(link):
                    continue

                # anchor links in a page should not be saved        
                index = link.find('#')
                if index != -1:
                    self.handle_anchor_links(link)
                else:
                    # append to private list of links
                    self.check_add_link(typ, link)

    def handle_data(self, data):
        # Set title only once
        if self._tag.lower()=='title' and self._pagetitle=='':
            self._pagetitle = data.strip()

    def check_add_link(self, typ, link):
        """ To avoid adding duplicate links """

        f = False

        if typ == 'image':
            if not (typ, link) in self.images:
                # moredebug('Adding image ', link, typ)
                self.images.append((typ, link))
        elif not (typ, link) in self.links:
                # moredebug('Adding link ', link, typ)
                pos = self.getpos()
                self.links.append((typ, link))
                self.linkpos[(typ,link)] = (pos[0],pos[1])
                

    def add_tag_info(self, taginfo):
        """ Add new tag information to this object.
        This can be used to change the behavior of this class
        at runtime by adding new tags """

        # The taginfo object should be a dictionary
        # of the form { tagtype : (elementname, elementype) }

        # egs: { 'body' : ('background', 'img) }
        if type(taginfo) != dict:
            raise AttributeError, "Attribute type mismatch, taginfo should be a dictionary!"

        # get the key of the dictionary
        key = (taginfo.keys())[0]
        if len(taginfo[key]) != 2:
            raise ValueError, 'Value mismatch, size of tag tuple should be 2'

        # get the value tuple
        tagelname, tageltype = taginfo[key]

        # see if this is an already existing tagtype
        if key in self.handled.keys:
            _values = self.handled[key]

            f=0
            for index in xrange(len(_values)):
                # if the elementname is also
                # the same, just replace it.
                v = _values[index]

                elname, eltype = v
                if elname == tagelname:
                    f=1
                    _values[index] = (tagelname, tageltype)
                    break

            # new element, add it to list
            if f==0: _values.append((tagelname, tageltype))
            return 0

        else:
            # new key, directly modify dictionary
            elements = []
            elements.append((tagelname, tageltype))
            self.handled[key] = elements 

    def reset(self):
        SGMLParser.reset(self)

        self.base = None
        self.links = []
        self.images = []
        self.base_href = False
        self.base_url = ''
        self.can_index = True
        self.can_follow = True
        
    def base_url_defined(self):
        """ Return whether this url had a
        base url of the form <base href='...'>
        defined """

        return self.base_href

    def get_base_url(self):
        return self.base


class HarvestManSGMLOpParser(HarvestManSimpleParser):
    """ A parser based on effbot's sgmlop """

    def __init__(self):
        # This module should be built already!
        import sgmlop
        self.parser = sgmlop.SGMLParser()
        self.parser.register(self)
        HarvestManSimpleParser.__init__(self)
        
    def finish_starttag(self, tag, attrs):
        self.unknown_starttag(tag, attrs)

    def feed(self, data):
        self.parser.feed(data)
        
class HarvestManCSSParser(object):
    """ Class to parse stylesheets and extract URLs """

    # Regexp to parse stylesheet imports
    importcss1 = re.compile(r'(\@import\s+\"?)(?!url)([\w.-:/]+)(\"?)', re.MULTILINE|re.LOCALE|re.UNICODE)
    importcss2 = re.compile(r'(\@import\s+url\(\"?)([\w.-:/]+)(\"?\))', re.MULTILINE|re.LOCALE|re.UNICODE)
    # Regexp to parse URLs inside CSS files
    cssurl = re.compile(r'(url\()([^\)]+)(\))', re.LOCALE|re.UNICODE)

    def __init__(self):
        # Any imported stylesheet URLs
        self.csslinks = []
        # All URLs including above
        self.links = []

    def feed(self, data):
        self._parse(data)
        
    def _parse(self, data):
        """ Parse stylesheet data and extract imported css links, if any """

        # Return is a list of imported css links.
        # This subroutine uses the specification mentioned at
        # http://www.w3.org/TR/REC-CSS2/cascade.html#at-import
        # for doing stylesheet imports.

        # This takes care of @import "style.css" and
        # @import url("style.css") and url(...) syntax.
        # Media types specified if any, are ignored.
        
        # Matches for @import "style.css"
        l1 = self.importcss1.findall(data)
        # Matches for @import url("style.css")
        l2 = self.importcss2.findall(data)
        # Matches for url(...)
        l3 = self.cssurl.findall(data)
        
        for item in (l1+l2):
            if not item: continue
            url = item[1].replace("'",'').replace('"','')
            self.csslinks.append(url)
            self.links.append(url)
            
        for item in l3:
            if not item: continue
            url = item[1].replace("'",'').replace('"','')
            self.links.append(url)

if __name__=="__main__":
    import os
    import config
    import logger
    
    InitConfig(config.HarvestManStateObject)
    InitLogger(logger.HarvestManLogger)
    
    cfg = GetObject('config')
    cfg.verbosity = 5
    SetLogSeverity()
    
    cfg.getquerylinks = True
    
    # p = HarvestManSimpleParser()
    p = HarvestManSGMLOpParser()
    
    urls = ['http://projecteuler.net/index.php?section=problems']
    urls = ['http://www.evvs.dk/index.php?cPath=30&osCsid=3b110c689f01d722dbbe53c5cee0bf2d']
    urls = ['http://nltk.sourceforge.net/lite/doc/api/nltk_lite.contrib.fst.draw_graph.GraphEdgeWidget-class.html']
    urls = ['http://wiki.java.net/bin/view/Javawsxml/Rome05Tutorials']
    
    for url in urls:
        if os.system('wget %s -O index.html' % url ) == 0:
            p.feed(open('index.html').read())
            print p.links
            for link in p.links:
                print link
            p.reset()

                                   




