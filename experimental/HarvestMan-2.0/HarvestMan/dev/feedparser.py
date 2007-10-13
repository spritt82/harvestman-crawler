# -- coding: latin-1
""" A simple RSS feed parser returning a list of links
in a given feed.

Created Anand B Pillai <abpillai@gmail.com> xx-xx-xxxx
Modified Anand B Pillai <abpillai@gmail.com> Apr 4 2007 Fixed stuff, added
                        function to get feeds from URL.

Copyright(C) 2007  Anand B Pillai

"""


import xml.parsers.expat
import urllib2

class FeedParser(object):

    def __init__(self):
        self._node = ''
        self.links = []
        
    def start_element(self, name, attrs):
       
        if not attrs:
            # If element has no attributes, the
            # value will be in CDATA. Store the
            # element name so that we can use it
            # in cdata callback.
            self._node = name
        
    def char_data(self, data):
        # This will be called after the
        # start element is called. If the
        # element is of interest, set it's
        # option.
        
        if self._node and data:
            # print 'Setting option for %s %s ' % (self._node, data)
            if self._node=='link':
                data = data.strip()
                if data:
                    try:
                        self.links.index(data)
                    except ValueError:
                        self.links.append(data)

def getFeedUrls(rssurl):
    """ Return feed URLs from the given rss URL """

    try:
        f = urllib2.urlopen(rssurl)
        data = f.read()
        p = xml.parsers.expat.ParserCreate()
        c = FeedParser()
    
        p.StartElementHandler = c.start_element
        p.CharacterDataHandler = c.char_data

        try:
            p.Parse(data)
        except xml.parsers.expat.ExpatError, e:
            print e

        return c.links
    except Exception, e:
        print e
        
    
if __name__=="__main__":
    print getFeedUrls('http://osnews.com/files/recent.xml')
    print getFeedUrls('http://www.technologyreview.com/rss/rss.aspx?z=316')    
