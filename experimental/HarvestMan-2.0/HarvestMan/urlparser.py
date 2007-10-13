# -- coding: latin-1
"""urlparser.py - Module to parse a URL string based
   on a directory/parent URL and extract useful information like
   directory, filename path etc. This module is part of
   the HarvestMan program.

   Author: Anand B Pillai <anand at harvestmanontheweb.com>

   Creation Date: Nov 2 2004


   Jan 01 2006      jkleven  Change is_webpage to return 'true'
                             if the URL looks like a form query.
   Jan 10 2006      Anand    Converted from dos to unix format (removed Ctrl-Ms).
   Oct 1 2006       Anand    Fixes for EIAO ticket #193 - added reduce_url
                             method to take care of .. chars inside URLs.

   Feb 25 2007      Anand    Added .ars as a web-page extension to support
                             the popular ars-technica website.
   Mar 12 2007      Anand    Added more fields for multipart. Fixed a bug in
                             is_webpage - anchor links should be returned
                             as web-page links.

   Apr 12 2007      Anand    Fixed a bug in anchor link parsing. The current
                             logic was not taking care of multiple anchor
                             links (#anchor1#anchor2). Fixed it by using
                             a regular expression.

                             Test page is
                             http://nltk.sourceforge.net/lite/doc/api/term-index.html
   
   Copyright (C) 2004 Anand B Pillai.
   
"""

__version__ = '2.0 b1'
__author__ = 'Anand B Pillai'

import os
import re
import mimetypes
import copy
import urlproc
import md5

from common.common import *
from urltypes import *

class HarvestManUrlParserError(Exception):

    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return self.__str__()
    
    def __str__(self):
        return str(self.value)
    
class HarvestManUrlParser(object):
    """ New HarvestMan Url Parser class re-written
    to make the code more readable """

    TEST = 0
    IDX = 0
    URLSEP = '/'
    PROTOSEP = '//'
    DOTDOT = '..'
    DOT = '.'
    PORTSEP = ':'
    BACKSLASH = '\\'

    protocol_map = { "http://" : 80,
                     "ftp://" : 21,
                     "https://" : 443,
                     "file://": 0
                   }

    # Popular image types file extensions
    image_extns = ('.bmp', '.dib', '.dcx', '.emf', '.fpx', '.gif', '.ico', '.img',
                   '.jp2', '.jpc', '.j2k', '.jpf', '.jpg', '.jpeg', '.jpe',
                   '.mng', '.pbm', '.pcd', '.pcx', '.pgm', '.png', '.ppm', 
                   '.psd', '.ras', '.rgb', '.tga', '.tif', '.tiff', '.wbmp',
                   '.xbm', '.xpm')

    # Most common web page url file extensions
    # including dynamic server pages & cgi scripts.
    webpage_extns = ('', '.htm', '.html', '.shtm', '.shtml', '.php',
                     '.php3','.php4','.asp', '.aspx', '.jsp','.psp','.pl',
                     '.cgi', '.stx', '.cfm', '.cfml', '.cms', '.ars')


    # Document extensions
    document_extns = ('.doc','.rtf','.odt','.odp','.ott','.sxw','.stw',
                      '.sdw','.vor','.xml','.pdf','.ps')

    # Web-page extensions which automatically default to directories
    # These are special web-page types which are web-pages as well
    # as directories. Most common example is the .ars file extension
    # of arstechnica.com.
    default_directory_extns = ('.ars',)
    
    # Most common stylesheet url file extensions
    stylesheet_extns = ( '.css', )

    # Regular expression for matching
    # urls which contain white spaces
    wspacere = re.compile(r'\w+\s+\w+')

    # Regular expression for anchor tags
    anchore = re.compile(r'\#+')
    
    # jkleven: Regex if we still don't recognize a URL address as HTML.  Only
    # to be used if we've looked at everything else and URL still isn't
    # a known type.  This regex is similar to one in pageparser.py but 
    # we changed a few '*' to '+' to get one or more matches.  
    form_re = re.compile(r'[-.:_a-zA-Z0-9]+\?[-.:_a-zA-Z0-9]+=[-.a:_-zA-Z0-9]*')

    # Junk chars
    junk_chars = ('?','*','"','<','>','!',':','/','\\')
    # Replacement chars
    junk_chars_repl = ('',)*len(junk_chars)

    # %xx char replacement regexp
    percent_repl = re.compile(r'\%[a-f0-9][a-f0-9]', re.IGNORECASE)

    # Special strings
    special_strings = ('%20','%7E','%2B','%22','%3C','%3E','%23','%25',
                       '%7B','%7D','%7C','%5C','%5E','%5B','%5D','%60')

    # Special string replacements
    special_strings_repl = (' ','~','+','"','<','>','#','%','{','}','|','\\','^','[',']','`')

    def reset_IDX(cls):
        HarvestManUrlParser.IDX = 0

    reset_IDX = classmethod(reset_IDX)
    
    def __init__(self, url, urltype = 'generic', cgi = False, baseurl  = None, rootdir = ''):

        # For saving original url
        # since self.url can get
        # modified
        self.origurl = url
        
        if url[-1] == self.URLSEP:
            self.url = url[:-1]
        else:
            self.url = url

        self.url = urlproc.modify_url(self.url)
        self.typ = urltype
        self.cgi = cgi
        self.anchor = ''
        self.index = 0
        self.filename = 'index.html'
        self.validfilename = 'index.html'
        self.lastpath = ''
        self.protocol = ''
        self.defproto = False
        # If the url is a file like url
        # this value will be true, if it is
        # a directory like url, this value will
        # be false.
        self.filelike = False
        # download status, a number indicating
        # whether this url was downloaded successfully
        # or not. 0 indicates a successful download, and
        # any number >0 indicates a failed download
        self.status = 0
        # Fatal status
        self.fatal = False
        # is starting url?
        self.starturl = False
        # Flag for files having extension
        self.hasextn = False
        # Relative path flags
        self.isrel = False
        # Relative to server?
        self.isrels = False
        self.port = 80
        self.domain = ''
        self.rpath = []
        # Recursion depth
        self.rdepth = 0
        # Content information for updating urls
        self.contentdict = {}
        # Url generation
        self.generation = 0
        # Url priority
        self.priority = 0
        # rules violation cache flags
        self.violatesrules = False
        self.rulescheckdone = False
        # Bytes range - used for HTTP/1.1
        # multipart downloads. This has to
        # be set to an xrange object 
        self.range = None
        # Flag to try multipart
        self.trymultipart = False
        # Multipart index
        self.mindex = 0
        # Original url for mirrored URLs
        self.mirror_url = ''
        # Flag set for URLs which are mirrored from
        # a different server than the original URL
        self.mirrored = False
        # Content-length for multi-part
        # This is the content length of the original
        # content.
        self.clength = 0
        self.dirpath = []
        # Archive for self.dirpath
        self.dirpathold = []
        # Archive for self.filename
        self.filenameold = 'index.html'
        self.validfilenameold = 'index.html'
        # Archive for self.rpath
        self.rpathold = []
        # Archive for self.domain
        self.domainold = ''
        # Re-computation flag
        self.reresolved = False
        self.baseurl = None
        # Hash of page data
        self.pagehash = ''
        # Flag for using old filename
        self.useoldfilename = False
        # Base Url Dictionary
        if baseurl:
            if isinstance(baseurl, HarvestManUrlParser):
                self.baseurl = baseurl
            elif type(baseurl) is str:
                self.baseurl = HarvestManUrlParser(baseurl, 'generic', cgi, None, rootdir)
                      
        # Root directory
        if rootdir == '':
            if self.baseurl and self.baseurl.rootdir:
                self.rootdir = self.baseurl.rootdir
            else:
                self.rootdir = os.getcwd()
        else:
            self.rootdir = rootdir
            
        self.anchorcheck()
        self.resolveurl()

    def re_init(self):
        """ Reinitialize some of the attributes """

        # Used by wrapper_resolveurl
        if self.url[-1] == self.URLSEP:
            self.url = self.url[:-1]
        else:
            self.url = self.url
        # Process URL
        self.url = urlproc.modify_url(self.url)
        self.lastpath = ''
        self.protocol = ''
        self.defproto = False
        self.hasextn = False
        self.isrel = False
        self.isrels = False
        self.port = 80
        self.domain = ''
        self.rpath = []
        # Recursion depth
        self.rdepth = 0
        self.dirpath = []
        self.rpath = []
        self.filename = 'index.html'
        self.validfilename = 'index.html'
        
    def wrapper_resolveurl(self):
        """ Called forcefully to re-resolve a URL """

        extrainfo("Re-resolving URL: Current is %s..." % self.get_full_url())
        # Make archives of everything
        self.dirpathold = self.dirpath[:]
        self.rpathold = self.rpath[:]
        self.filenameold = self.filename[:]
        self.validfilenameold = self.validfilename[:]
        self.domainold = self.domain[:]
        self.re_init()
        
        self.anchorcheck()
        self.resolveurl()
        self.reresolved = True
        extrainfo("Re-resolving URL: New is %s..." % self.get_full_url())
        
    def anchorcheck(self):
        """ Checking for anchor tags and processing accordingly """

        if self.typ == 'anchor':
            if not self.baseurl:
                raise HarvestManUrlParserError, 'Base url should not be empty for anchor type url'

            if '#' in self.url:
                # Split with re
                items = self.anchore.split(self.url)
                # First item is the original url
                if len(items):
                    if items[0]:
                        self.url = items[0]
                    else:
                        self.url = self.baseurl.get_full_url()
                    # Rest forms the anchor tag
                    self.anchor = '#' + '#'.join(items[1:])
                    
            #index = self.url.rfind('#')
            #if index != -1:
            #    newhref = self.url[:index]
            #    self.anchor = self.url[index:]
            #    if newhref:
            #        self.url = newhref
            #    else:
            #        self.url = self.baseurl.get_full_url()

        else:
            pass

    def resolve_protocol(self):
        """ Resolve the protocol of the url """

        url2 = self.url.lower()
        for proto in self.protocol_map.keys():
            if url2.find(proto) != -1:
                self.protocol = proto
                self.port = self.protocol_map.get(proto)
                return True
        else:
            # Fix: Use regex for detecting WWW urls.
            # Check for WWW urls. These can begin
            # with a 'www.' or 'www' followed by
            # a single number (www1, www3 etc).
            wwwre = re.compile(r'^www(\d?)\.')

            if wwwre.match(url2):
                self.protocol = 'http://'
                self.url =  "".join((self.protocol, self.url))
                return True
            
            # Urls relative to server might
            # begin with a //. Then prefix the protocol
            # string to them.
            if self.url.find('//') == 0:
                # Pick protocol from base url
                if self.baseurl and self.baseurl.protocol:
                    self.protocol = self.baseurl.protocol
                else:
                    self.protocol = "http://"   
                self.url = "".join((self.protocol, self.url[2:]))
                return True

            # None of these
            # Protocol not resolved, so check
            # base url first, if not found, set
            # default protocol...
            if self.baseurl and self.baseurl.protocol:
                self.protocol = self.baseurl.protocol
            else:
                self.protocol = 'http://'

            self.defproto = True
        
            return False
        
    def resolveurl(self):
        """ Resolves the url finding out protocol, port, domain etc
        . Also resolves relative paths and builds a local file name
        for the url based on the root directory path """

        if len(self.url)==0:
            raise HarvestManUrlParserError, 'Error: Zero Length Url'

        proto = self.resolve_protocol()

        paths = ''
        
        if not proto:
            # Could not resolve protocol, must be a relative url
            if not self.baseurl:
                raise HarvestManUrlParserError, 'Base url should not be empty for relative urls'

            # Set url-relative flag
            self.isrel = True
            # Is relative to server?
            if self.url[0] == '/':
                self.isrels = True
            
            # Split paths
            relpaths = self.url.split(self.URLSEP)
            try:
                idx = relpaths.index(self.DOTDOT)
            except ValueError:
                idx = -1

            # Only reduce if the URL itself does not start with
            # .. - if it does our rpath algorithm takes
            # care of it.
            if idx > 0:
                relpaths = self.reduce_url(relpaths)
            
            # Build relative path by checking for "." and ".." strings
            self.rindex = 0
            for ritem in relpaths:
                # If path item is ., .. or empty, increment
                # relpath index.
                if ritem in (self.DOT, self.DOTDOT, ""):
                    self.rindex += 1
                    # If path item is not empty, insert
                    # to relpaths list.
                    if ritem:
                        self.rpath.append(ritem)

                else:
                    # Otherwise, add the rest to paths
                    # with the separator
                    for entry in relpaths[self.rindex:]:
                        paths = "".join((paths, entry, self.URLSEP))

                    # Remove the last entry
                    paths = paths[:-1]
                    
                    # Again Trim if the relative path ends with /
                    # like href = /img/abc.gif/ 
                    if paths[-1] == '/':
                        paths = paths[:-1]
                    break
            
        else:
            # Absolute path, so 'paths' is the part of it
            # minus the protocol part.
            paths = self.url.replace(self.protocol, '')            

            # Split URL
            items = paths.split(self.URLSEP)
            
            # If there are nonsense .. and . chars in the paths, remove
            # them to construct a sane path.
            #try:
            #    idx = items.index(self.DOTDOT)
            #except ValueError:
            #    idx = -1            
            flag = (self.DOT in items) or (self.DOTDOT in items)
            
            if flag:
                # Bugfix: Do not allow a URL like http://www.foo.com/../bar
                # to become http://bar. Basically if the index of .. is
                # 1, then remove the '..' entirely. This bug was encountered
                # in EIAO testing of http://www.fylkesmannen.no/ for the URL
                # http://www.fylkesmannen.no/osloogakershu
                
                items = self.reduce_url(items)
                # Re-construct URL
                paths = self.URLSEP.join(items)
                
        # Now compute local directory/file paths

        # For cgi paths, add a url separator at the end 
        #if self.cgi:
        #    paths = "".join((paths, self.URLSEP))

        self.compute_dirpaths(paths)
        self.compute_domain_and_port()

        # For some file extensions, automatically set as directory URL.
        if self.validfilename:
            extn = ((os.path.splitext(self.validfilename))[1]).lower()
            if extn in self.default_directory_extns:
                self.set_directory_url()

    def reduce_url(self, paths):
        """ Remove nonsense .. and . chars from URL paths """
        
        for x in range(len(paths)):
            path = paths[x]
            try:
                nextpath = paths[x+1]
                if nextpath == '..':
                    paths.pop(x+1)
                    # Do not allow to remove the domain for
                    # stupid URLs like 'http://www.foo.com/../bar' or
                    # 'http://www.foo.com/camp/../../bar'. If allowed
                    # they become nonsense URLs like http://bar.

                    # This bug was encountered in EIAO testing of
                    # http://www.fylkesmannen.no/ for the URL
                    # http://www.fylkesmannen.no/osloogakershu
                    
                    if self.isrel or x>0:
                        paths.remove(path)
                    return self.reduce_url(paths)
                elif nextpath=='.':
                    paths.pop(x+1)
                    return self.reduce_url(paths)                    
            except IndexError:
                return paths
        
        
    def compute_file_and_dir_paths(self):
        """ Compute file and directory paths """

        
        if self.lastpath:
            dotindex = self.lastpath.find(self.DOT)
            if dotindex != -1:
                self.hasextn = True

            # If there is no extension or if there is
            # an extension which is occuring in the middle
            # of last path...
            if (dotindex == -1) or \
                ((dotindex >0) and (dotindex < (len(self.lastpath)-1))):
                self.filelike = True
                # Bug fix - Strip leading spaces & newlines
                self.validfilename =  self.make_valid_filename(self.lastpath.strip())
                self.filename = self.lastpath.strip()
                self.dirpath  = self.dirpath [:-1]
        else:
            if not self.isrel:
                self.dirpath  = self.dirpath [:-1]

        # Remove leading spaces & newlines from dirpath
        dirpath2 = []
        for item in self.dirpath:
            dirpath2.append(item.strip())

        # Copy
        self.dirpath = dirpath2[:]
            
    def compute_dirpaths(self, path):
        """ Computer local file & directory paths for the url """

        self.dirpath = path.split(self.URLSEP)
        self.lastpath = self.dirpath[-1]

        if self.isrel:
            # Construct file/dir names - This is valid only if the path
            # has more than one component - like www.python.org/doc .
            # Otherwise, the url is a plain domain
            # path like www.python.org .
            self.compute_file_and_dir_paths()

            # Interprets relative path
            # ../../. Nonsense relative paths are graciously ignored,
            self.rpath.reverse()
            if len(self.rpath) == 0 :
                if not self.rindex:
                    self.dirpath = self.baseurl.dirpath + self.dirpath
            else:
                pathstack = self.baseurl.dirpath[0:]
                
                for ritem in self.rpath:
                    if ritem == self.DOT:
                        pathstack = self.baseurl.dirpath[0:]
                    elif ritem == self.DOTDOT:
                        if len(pathstack) !=0:
                            pathstack.pop()
            
                self.dirpath  = pathstack + self.dirpath 
                
            # Support for NONSENSE relative paths such as
            # g/../foo and g/./foo 
            # consider base = http:\\bar.com\bar1
            # then g/../foo => http:\\bar.com\bar1\..\foo => http:\\bar.com\foo
            # g/./foo  is utter nonsense and we feel free to ignore that.
            index = 0
            for item in self.dirpath:
                if item in (self.DOT, self.DOTDOT):
                    self.dirpath.remove(item)
                if item == self.DOTDOT:
                    self.dirpath.remove(self.dirpath[index - 1])
                index += 1
        else:
            if len(self.dirpath) > 1:
                self.compute_file_and_dir_paths()
            
    def compute_domain_and_port(self):
        """ Computes url domain and port &
        re-computes if necessary """

        # Resolving the domain...
        
        # Domain is parent domain, if
        # url is relative :-)
        if self.isrel:
            self.domain = self.baseurl.domain
        else:
            # If not relative, then domain
            # if the first item of dirpath.
            self.domain=self.dirpath[0]
            self.dirpath = self.dirpath[1:]

        # Find out if the domain contains a port number
        # for example, server:8080
        dom = self.domain
        index = dom.find(self.PORTSEP)
        if index != -1:
            self.domain = dom[:index]
            # A bug here => needs to be fixed
            try:
                self.port   = int(dom[index+1:])
            except:
                pass

        # Now check if the base domain had a port specification (other than 80)
        # Then we need to use that port for all its children, otherwise
        # we can use default value.
        if self.isrel and \
               self.baseurl and \
               self.baseurl.port != self.port and\
               self.baseurl.protocol != 'file://':
            
            self.port = self.baseurl.port

    def make_valid_filename(self, s):
        """ Replace junk characters to create a valid
        filename """

        #for x,y in zip(self.special_strings, self.special_strings_repl):
        #    s = s.replace(x, y).replace(x.lower(), y)
        # Replace any %xx strings
        percent_chars = self.percent_repl.findall(s)
        for pchar in percent_chars:
            s = s.replace(pchar, chr(int(pchar.replace('%','0x'), 16)))
            
        for x,y in zip(self.junk_chars, self.junk_chars_repl):
            s = s.replace(x, y)

        #for x in self.junk_chars:
        #    s = s.replace(x, '\\' + x)

        return s

    def make_valid_url(self, url):
        """ Make a valid url """

        # Replace spaces between words
        # with '%20'.
        # For example http://www.foo.com/bar/this file.html
        # Fix: Use regex instead of blind
        # replacement.
        if self.wspacere.search(url):
            url = re.sub(r'\s', '%20', url)
            
        return url

    # ============ Begin - Is (Boolean Get) Methods =========== #
    def is_filename_url(self):
        """ Return whether this is file name url """

        # A directory url is something like http://www.python.org
        # which points to the <index.html> file inside the www.python.org
        # directory.A file name url is a url that points to an actual
        # file like http://www.python.org/doc/current/tut/tut.html

        return self.filelike

    def is_cgi(self):
        """ Check whether this url is a cgi (dynamic/form) link """

        return self.cgi

    def is_relative_path(self):
        """ Return whether the original url was a relative one """

        return self.isrel

    def is_relative_to_server(self):
        """ Return whether the original url was relative to the server """
        
        return self.isrels

    def is_image(self):
        """ Find out by filename extension if the file is an image """

        if self.typ == 'image':
            return True
        elif self.typ == 'generic':
            if self.validfilename:
                extn = ((os.path.splitext(self.validfilename))[1]).lower()
                if extn in self.image_extns:
                    return True
             
        return False
            
    def is_webpage(self):
        """ Find out by filename extension if the file <filename>
        is an html or html-like (server-side dynamic html files)
        file, or a candidate for one """

        # Note: right now we treat dynamic server-side scripts namely
        # php, psp, asp, pl, jsp, and cgi as possible html candidates, though
        # actually they might be generating non-html content (like dynamic
        # images.)
        
        if self.typ.isA(TYPE_WEBPAGE):
            return True
        elif self.typ==TYPE_ANY:
            if self.validfilename:
                extn = ((os.path.splitext(self.validfilename))[1]).lower()
                
                if extn in self.webpage_extns:
                    return True
                
                elif extn not in self.document_extns and extn not in self.image_extns:
                    return True
                else:
                    # jkleven: 10/1/06.  Forms were never being parsed for links.

                    # If we are allowing download of query forms (i.e., bin?asdf=3 style URLs)
                    # then run the URL through a regex if we're still not sure if its ok.
                    # if it matches the from_re precompiled regex then we'll assume its
                    # a query style URL and we'll return true.
                    cfg = GetObject('config')
                    if cfg.getquerylinks and self.form_re.search(self.get_full_url()):                 
                        return True

        return False

    def is_stylesheet(self):
        """ Find out whether the url is a style sheet type """

        if self.typ == 'stylesheet':
            return True
        elif self.typ == 'generic':
            if self.validfilename:
                extn = ((os.path.splitext(self.validfilename))[1]).lower()
                if extn in self.stylesheet_extns:
                    return True
             
        return False

    def is_document(self):
        """ Return whether the url is a document """

        # This method is useful for Indexers which use HarvestMan.
        # We define any URL which is not an image, is either a web-page
        # or any of the following types as a document.

        # Microsoft word documents
        # Openoffice documents
        # Adobe PDF documents
        # Postscript documents

        if self.is_image(): return False
        if self.is_webpage(): return True

        # Check extension
        if self.validfilename:
            extn = ((os.path.splitext(self.validfilename))[1]).lower()
            if extn in self.document_extns:
                return True

        return False
    
    def is_equal(self, url):
        """ Find whether the passed url matches
        my url """

        # Try 2 tests, one straightforward
        # other with a "/" appended at the end
        myurl = self.get_full_url()
        if url==myurl:
            return True
        else:
            myurl += self.URLSEP
            if url==myurl:
                return True

        return False
        
    # ============ End - Is (Boolean Get) Methods =========== #  
    # ============ Begin - General Get Methods ============== #
    def get_url_content_info(self):
        """ Get the url content information """
        
        return self.contentdict
    
    def get_anchor(self):
        """ Return the anchor tag of this url """

        return self.anchor

    def get_anchor_url(self):
        """ Get the anchor url, if this url is an anchor type """

        return "".join((self.get_full_url(), self.anchor))

    def get_generation(self):
        """ Return the generation of this url """
        
        return self.generation    

    def get_priority(self):
        """ Get the priority for this url """

        return self.priority

    def get_download_status(self):
        """ Return the download status for this url """

        return self.status

    def get_type(self):
        """ Return the type of this url as a string """
        
        return self.typ

    def get_base_urlobject(self):
        """ Return the base url object of this url """
        
        return self.baseurl

    def get_original_url_directory(self):
        """ Return the directory path (url minus its filename if any) of the
        original URL """

        # Return only if this was recomputer
        # get the directory path of the url
        fulldom = self.get_full_domain()
        urldir = fulldom

        if self.dirpathold:
            newpath = "".join((self.URLSEP, "".join([ x+'/' for x in self.dirpathold])))
            urldir = "".join((fulldom, newpath))

        return urldir
    
    def get_url_directory(self):
        """ Return the directory path (url minus its filename if any) of the url """
        
        # get the directory path of the url
        fulldom = self.get_full_domain()
        urldir = fulldom

        if self.dirpath:
            newpath = "".join((self.URLSEP, "".join([ x+'/' for x in self.dirpath])))
            urldir = "".join((fulldom, newpath))

        return urldir

    def get_url_directory_sans_domain(self):
        """ Return url directory minus the domain """

        # New function in 1.4.1
        urldir = ''
        
        if self.dirpath:
            urldir = "".join((self.URLSEP, "".join([ x+'/' for x in self.dirpath])))

        return urldir        
        
    def get_url(self):
        """ Return the url of this object """
        
        return self.url

    def get_original_url(self):
        """ Return the original url of this object """
        
        return self.origurl
    
    def get_full_url(self):
        """ Return the full url path of this url object after
        resolving relative paths, filenames etc """

        rval = self.get_full_domain_with_port()
        if self.dirpath:
            newpath = "".join([ x+self.URLSEP for x in self.dirpath if x and not x[-1] ==self.URLSEP])
            rval = "".join((rval, self.URLSEP, newpath))
            
        if rval[-1] != self.URLSEP:
            rval += self.URLSEP

        if self.filelike:
            rval = "".join((rval, self.filename))
            
        return self.make_valid_url(rval)

    def get_full_url_sans_port(self):
        """ Return absolute url without the port number """

        rval = self.get_full_domain()
        if self.dirpath:
            newpath = "".join([ x+'/' for x in self.dirpath])
            rval = "".join((rval, self.URLSEP, newpath))

        if rval[-1] != self.URLSEP:
            rval += self.URLSEP

        if self.filelike:
            rval = "".join((rval, self.filename))

        return self.make_valid_url(rval)

    def get_port_number(self):
        """ Return the port number of this url """

        # 80 -> http urls
        return self.port

    def get_relative_url(self):
        """ Return relative path of url w.r.t the domain """

        newpath=""
        if self.dirpath:
            newpath =  "".join(("/", "".join([ x+'/' for x in self.dirpath])))

        if self.filelike:
            newpath = "".join((newpath, self.URLSEP, self.filename))
            
        return self.make_valid_url(newpath)

    def get_base_domain(self):
        """ Return the base domain for this url object """

        # Explanation: Base domain is the domain
        # at the root of a given domain. For example
        # base domain of stats.foo.com is foo.com.
        # If there is no subdomain, this will be
        # the same as the domain itself.

        # If the server name is of the form say bar.foo.com
        # or vodka.bar.foo.com, i.e there are more than one
        # '.' in the name, then we need to return the
        # last string containing a dot in the middle.

        # Get domain
        domain = self.domain
        
        if domain.count('.') > 1:
            dotstrings = domain.split('.')
            # now the list is of the form => [vodka, bar, foo, com]

            # Return the last two items added with a '.'
            # in between
            return "".join((dotstrings[-2], ".", dotstrings[-1]))
        else:
            # The server is of the form foo.com or just "foo"
            # so return it straight away
            return domain

    def get_base_domain_with_port(self):
        """ Return the base domain (server) with port number
        appended to it, if the port number is not the
        default for the current protocol """
        
        if ((self.protocol == 'http://' and int(self.port) != 80) \
            or (self.protocol == 'https://' and int(self.port) != 443) \
            or (self.protocol == 'ftp://' and int(self.port) != 21)):
            return self.get_base_domain() + ':' + str(self.port)
        else:
            return self.get_base_domain()

    def get_url_hash(self):
        """ Return a hash value for the URL """

        m = md5.new()
        m.update(self.get_full_url())
        return str(m.hexdigest())
    
    def get_domain_hash(self):
        """ Return the hask value for the domain """

        m = md5.new()
        m.update(self.get_full_domain())
        return str(m.hexdigest())

    def get_data_hash(self):
        """ Return the hash value for the URL data """

        return self.pagehash

    def get_domain(self):
        """ Return the domain (server) for this url object """
        
        return self.domain

    def get_full_domain(self):
        """ Return the full domain (protocol + domain) for this url object """
        
        return self.protocol + self.domain

    def get_full_domain_with_port(self):
        """ Return the domain (server) with port number
        appended to it, if the port number is not the
        default for the current protocol """

        if (self.protocol == 'http://' and int(self.port) != 80) \
           or (self.protocol == 'https://' and int(self.port) != 443) \
           or (self.protocol == 'ftp://' and int(self.port) != 21):
            return self.get_full_domain() + ':' + str(self.port)
        else:
            return self.get_full_domain()

    def get_domain_with_port(self):
        """ Return the domain (server) with port number
        appended to it, if the port number is not the
        default for the current protocol """

        if (self.protocol == 'http://' and self.port != 80) \
           or (self.protocol == 'https://' and self.port != 443) \
           or (self.protocol == 'ftp://' and self.port != 21):
            return self.domain + ':' + str(self.port)
        else:
            return self.domain

    def get_full_filename(self):
        """ Return the full filename of this url on the disk.
        This is created w.r.t the local directory where we save
        the url data """

        if self.useoldfilename:
            return self.get_full_filename_old()
        
        if not self.__class__.TEST:
            cfg = GetObject('config')
            if cfg.rawsave:
                return self.get_filename()
            else:
                return os.path.join(self.get_local_directory(), self.get_filename())
        else:
            return os.path.join(self.get_local_directory(), self.get_filename())            

    def get_full_filename_old(self):
        """ Return the old full filename of this url on the disk.
        This is created w.r.t the local directory where we save
        the url data """

        if not self.__class__.TEST:
            cfg = GetObject('config')
            if cfg.rawsave:
                return self.get_filename_old()
            else:
                return os.path.join(self.get_local_directory_old(), self.get_filename_old())
        else:
            return os.path.join(self.get_local_directory_old(), self.get_filename_old())            

    def get_filename(self):
        """ Return the filename of this url on the disk. """

        if self.useoldfilename:
            return self.validfilenameold
        
        # NOTE: This is just the filename, not the absolute filename path
        if not self.filelike:
            self.validfilename = 'index.html'
            
        return self.validfilename

    def get_filename_old(self):
        """ Return the old filename of this url on the disk. """

        # NOTE: This is just the filename, not the absolute filename path
        return self.validfilenameold
    
    def get_relative_filename(self, filename=''):

        # NOTE: Rewrote this method completely
        # on Nov 18 for 1.4 b2.
        
        # If no file name given, file name
        # is the file name of the parent url
        if not filename:
            if self.baseurl:
                filename = self.baseurl.get_full_filename()

        # Still filename is NULL,
        # return my absolute path
        if not filename:
            return self.get_full_filename()
        
        # Get directory of 'filename'
        diry = os.path.dirname(filename)
        if diry[-1] != os.sep:
            diry += os.sep
            
        # Get my filename
        myfilename = self.get_full_filename()
        # If the base domains are different, we
        # cannot find a relative path, so return
        # my filename itself.
        bdomain = self.baseurl.get_domain()
        mydomain = self.get_domain()

        if mydomain != bdomain:
            return myfilename

        # If both filenames are the same,
        # return just the filename.
        if myfilename==filename:
            return self.get_filename()
        
        # Get common prefix of my file name &
        # other file name.
        prefix = os.path.commonprefix([myfilename, filename])
        relfilename = ''
        
        if prefix:
            if not os.path.exists(prefix):
                prefix = os.path.dirname(prefix)
            
            if prefix[-1] != os.sep:
                prefix += os.sep

            # If prefix is the name of the project
            # directory, both files have no
            # common component.
            try:
                if os.path.samepath(prefix,self.rootdir):
                    return myfilename
            except:
                if prefix==self.rootdir:
                    return myfilename
            
            # If my directory is a subdirectory of
            # 'dir', then prefix should be the same as
            # 'dir'.
            sub=False

            # To test 'sub-directoriness', check
            # whether dir is wholly contained in
            # prefix. 
            prefix2 = os.path.commonprefix([diry,prefix])
            if prefix2[-1] != os.sep:
                prefix2 += os.sep
            
            # os.path.samepath is not avlbl in all
            # platforms.
            try:
                if os.path.samepath(diry, prefix2):
                    sub=True
            except:
                if diry==prefix2:
                    sub=True

            # If I am in a sub-directory, relative
            # path is my filename minus the common
            # path.
            if sub:
                relfilename = myfilename.replace(prefix2, '')
                return relfilename
            else:
                # If I am not in sub-directory, then
                # we need to get the relative path.
                dirwithoutprefix = diry.replace(prefix, '')
                filewithoutprefix = myfilename.replace(prefix, '')
                relfilename = filewithoutprefix
                    
                paths = dirwithoutprefix.split(os.sep)
                for item in paths:
                    if item:
                        relfilename = "".join(('..', os.sep, relfilename))

                return relfilename
        else:
            # If there is no common prefix, then
            # it means me and the passed filename
            # have no common paths, so return my
            # full path.
            return myfilename
            
    def get_relative_depth(self, hu, mode=0):
        """ Get relative depth of current url object vs passed url object.
        Return a postive integer if successful and -1 on failure """

        # Fixed 2 bugs on 22/7/2003
        # 1 => passing arguments to find function in wrong order
        # 2 => Since we allow the notion of zero depth, even zero
        # value of depth should be returned.

        # This mode checks for depth based on a directory path
        # This check is valid only if dir2 is a sub-directory of dir1
        dir1=self.get_url_directory()
        dir2=hu.get_url_directory()

        # spit off the protocol from directories
        dir1 = dir1.replace(self.protocol, '')
        dir2 = dir2.replace(self.protocol, '')      

        # Append a '/' to the dirpath if not already present
        if dir1[-1] != '/': dir1 += '/'
        if dir2[-1] != '/': dir2 += '/'

        if mode==0:
            # check if dir2 is present in dir1
            # bug: we were passing arguments to the find function
            # in the wrong order.
            if dir1.find(dir2) != -1:
                # we need to check for depth only if the above condition is true.
                l1=dir1.split('/')
                l2=dir2.split('/')
                if l1 and l2:
                    diff=len(l1) - len(l2)
                    if diff>=0: return diff

            return -1
        # This mode checks for depth based on the base server(domain).
        # This check is valid only if dir1 and dir2 belong to the same
        # base server (checked by name)
        elif mode==1:
            if self.domain == hu.domain:
                # we need to check for depth only if the above condition is true.
                l1=dir1.split('/')
                l2=dir2.split('/')
                if l1 and l2:
                    diff=len(l1) - len(l2)
                    if diff>=0: return diff
            return -1

        # This check is done for the current url against current base server (domain)
        # i.e, this mode does not use the argument 'hu'
        elif mode==2:
            dir2 = self.domain
            if dir2[-1] != '/':
                dir2 += '/'

            # we need to check for depth only if the above condition is true.
            l1=dir1.split('/')
            l2=dir2.split('/')
            if l1 and l2:
                diff=len(l1) - len(l2)
                if diff>=0: return diff
            return -1

        return -1

    def get_root_dir(self):
        """ Return root directory """
        
        return self.rootdir
    
    def get_local_directory(self):
        """ Return the local directory path of this url w.r.t
        the directory on the disk where we save the files of this url """
        
        # Gives Local Direcory path equivalent to URL Path in server
        rval = os.path.join(self.rootdir, self.domain)

        for diry in self.dirpath:
            if not diry: continue
            rval = os.path.abspath( os.path.join(rval, self.make_valid_filename(diry)))

        return os.path.normpath(rval)

    def get_local_directory_old(self):
        """ Return the old local directory path of this url w.r.t
        the directory on the disk where we save the files of this url """
        
        # Gives Local Direcory path equivalent to URL Path in server
        rval = os.path.join(self.rootdir, self.domainold)

        for diry in self.dirpathold:
            if not diry: continue
            rval = os.path.abspath( os.path.join(rval, self.make_valid_filename(diry)))

        return os.path.normpath(rval)    

    # ============ Begin - Set Methods =========== #

    def set_index(self):
        """ Set the index of this url object """
        
        HarvestManUrlParser.IDX += 1
        self.index = HarvestManUrlParser.IDX

    def set_directory_url(self):
        """ Set this as a directory url """

        self.filelike = False
        if self.dirpath and (self.dirpath[-1] != self.lastpath):
            self.dirpath.append(self.lastpath)
        self.validfilename = 'index.html'
        
    def set_url_content_info(self, headers):
        """ This function sets the url content information of this
        url. It is a convenient function which can be used by connectors
        to store url content information """

        if headers:
            self.contentdict = copy.deepcopy(headers)

    def violates_rules(self):
        """ Check if this url violates existing download rules """

        # If I am the base url object, violates rule checks apply
        # only if my original URL has changed.
        if self.index==0:
            if not self.reresolved:
                return False
            
        if not self.rulescheckdone:
            self.violatesrules = GetObject('ruleschecker').violates_basic_rules(self)
            self.rulescheckdone = True

        return self.violatesrules

    def recalc_locations(self):
        """ Recalculate filenames/directories etc """

        # Case 1 - trying to save as a file when the
        # parent "directory" is an existing file.
        # Solution - Change the paths of parent URL object
        # to change its filename...
        directory = self.get_url_directory()
        if os.path.isfile(directory):
            parent = self.baseurl
            # Anything can be done on this only if this
            # is a HarvestManUrlParser object
            if isinstance(parent, HarvestManUrlParser):
                parent.dirpath.append(parent.filename)
                parent.filename = 'index.html'
                parent.validfilename = 'index.html'

        # Case 2 - trying to save as file when the
        # path is an existing directory.
        # Solution - Save as index.html in the directory
        filename = self.get_full_filename()
        if os.path.isdir(filename):
            self.dirpath.append(self.filename)
            self.filename = 'index.html'
            self.validfilename = 'index.html'
        
    def manage_content_type(self, content_type):
        """ This function gets called from connector modules
        connect method, after retrieving information about
        a url. This function can manage the content type of
        the url object if there are any differences between
        the assumed type and the returned type """

        # Guess extension of type
        extn = mimetypes.guess_extension(content_type)
        
        if extn:
            if extn in self.webpage_extns:
                self.typ = TYPE_WEBPAGE
            elif extn in self.image_extns:
                self.typ = TYPE_IMAGE
            elif extn in self.stylesheet_extns:
                self.typ = TYPE_STYLESHEET
            else:
                self.typ = TYPE_FILE
        else:
            if content_type:
                # Do some generic tests
                klass, typ = content_type.split('/')
                if klass == 'image':
                    self.typ = TYPE_IMAGE
                elif typ == 'html':
                    self.typ = TYPE_WEBPAGE
            else:
                # Do static checks
                if self.is_webpage():
                    self.typ = TYPE_WEBPAGE
                elif self.is_image():
                    self.typ = TYPE_IMAGE
                elif self.is_stylesheet():
                    self.typ = TYPE_STYLESHEET
                else:
                    self.typ = TYPE_FILE

    # ============ End - Set Methods =========== #


if __name__=="__main__":
    import config
    import logger
    
    InitConfig(config.HarvestManStateObject)
    InitLogger(logger.HarvestManLogger)
    
    # Test code

    HarvestManUrlParser.TEST = 1
    hulist = [ HarvestManUrlParser('http://www.yahoo.com/photos/my photo.gif'),
               HarvestManUrlParser('http://www.rediff.com:80/r/r/tn2/2003/jun/25usfed.htm'),
               HarvestManUrlParser('http://cwc2003.rediffblogs.com'),
               HarvestManUrlParser('/sports/2003/jun/25beck1.htm',
                                   'generic', 0, 'http://www.rediff.com', ''),
               HarvestManUrlParser('ftp://ftp.gnu.org/pub/lpf.README'),
               HarvestManUrlParser('http://www.python.org/doc/2.3b2/'),
               HarvestManUrlParser('//images.sourceforge.net/div.png',
                                   'image', 0, 'http://sourceforge.net', ''),
               HarvestManUrlParser('http://pyro.sourceforge.net/manual/LICENSE'),
               HarvestManUrlParser('python/test.htm', 'generic', 0,
                                   'http://www.foo.com/bar/index.html', ''),
               HarvestManUrlParser('/python/test.css', 'generic',
                                   0, 'http://www.foo.com/bar/vodka/test.htm', ''),
               HarvestManUrlParser('/visuals/standard.css', 'generic', 0,
                                   'http://www.garshol.priv.no/download/text/perl.html',
                                   'd:/websites'),
               HarvestManUrlParser('www.fnorb.org/index.html', 'generic',
                                   0, 'http://pyro.sourceforge.net',
                                   'd:/websites'),
               HarvestManUrlParser('http://profigure.sourceforge.net/index.html',
                                   'generic', 0, 'http://pyro.sourceforge.net',
                                   'd:/websites'),
               HarvestManUrlParser('#anchor', 'anchor', 0, 
                                   'http://www.foo.com/bar/index.html',
                                   'd:/websites'),
               HarvestManUrlParser('nltk_lite.contrib.fst.draw_graph.GraphEdgeWidget-class.html#__init__#index-after', 'anchor', 0, 'http://nltk.sourceforge.net/lite/doc/api/term-index.html', 'd:/websites'),               
               HarvestManUrlParser('../../icons/up.png', 'image', 0,
                                   'http://www.python.org/doc/current/tut/node2.html',
                                   ''),
               HarvestManUrlParser('../eway/library/getmessage.asp?objectid=27015&moduleid=160',
                                   'generic',0,'http://www.eidsvoll.kommune.no/eway/library/getmessage.asp?objectid=27015&moduleid=160'),
               HarvestManUrlParser('fileadmin/dz.gov.si/templates/../../../index.php',
                                   'generic',0,'http://www.dz-rs.si','~/websites'),
               HarvestManUrlParser('http://www.evvs.dk/index.php?cPath=26&osCsid=90207c4908a98db6503c0381b6b7aa70','form',True,'http://www.evvs.dk'),
               HarvestManUrlParser('http://arstechnica.com/reviews/os/macosx-10.4.ars')]
                                  
                                  
    l = [ HarvestManUrlParser('http://www.yahoo.com/photos/my photo.gif'),
          HarvestManUrlParser('http://www.rediff.com:80/r/r/tn2/2003/jun/25usfed.htm'),
          HarvestManUrlParser('http://cwc2003.rediffblogs.com'),
          HarvestManUrlParser('/sports/2003/jun/25beck1.htm',
                              'generic', 0, 'http://www.rediff.com', ''),
          HarvestManUrlParser('ftp://ftp.gnu.org/pub/lpf.README'),
          HarvestManUrlParser('http://www.python.org/doc/2.3b2/'),
          HarvestManUrlParser('//images.sourceforge.net/div.png',
                              'image', 0, 'http://sourceforge.net', ''),
          HarvestManUrlParser('http://pyro.sourceforge.net/manual/LICENSE'),
          HarvestManUrlParser('python/test.htm', 'generic', 0,
                              'http://www.foo.com/bar/index.html', ''),
          HarvestManUrlParser('/python/test.css', 'generic',
                              0, 'http://www.foo.com/bar/vodka/test.htm', ''),
          HarvestManUrlParser('/visuals/standard.css', 'generic', 0,
                              'http://www.garshol.priv.no/download/text/perl.html'),
          HarvestManUrlParser('www.fnorb.org/index.html', 'generic',
                              0, 'http://pyro.sourceforge.net'),
          HarvestManUrlParser('http://profigure.sourceforge.net/index.html',
                              'generic', 0, 'http://pyro.sourceforge.net'),
          HarvestManUrlParser('#anchor', 'anchor', 0, 
                              'http://www.foo.com/bar/index.html'),
          HarvestManUrlParser('nltk_lite.contrib.fst.draw_graph.GraphEdgeWidget-class.html#__init__#index-after', 'anchor', 0, 'http://nltk.sourceforge.net/lite/doc/api/term-index.html'),              
          HarvestManUrlParser('../icons/up.png', 'image', 0,
                              'http://www.python.org/doc/current/tut/node2.html',
                              ''),
          HarvestManUrlParser('../eway/library/getmessage.asp?objectid=27015&moduleid=160',
                              'generic',0,'http://www.eidsvoll.kommune.no/eway/library/getmessage.asp?objectid=27015&moduleid=160'),
          HarvestManUrlParser('fileadmin/dz.gov.si/templates/../../../index.php',
                              'generic',0,'http://www.dz-rs.si'),
          HarvestManUrlParser('http://www.evvs.dk/index.php?cPath=26&osCsid=90207c4908a98db6503c0381b6b7aa70','form',True,'http://www.evvs.dk'),
          HarvestManUrlParser('http://arstechnica.com/reviews/os/macosx-10.4.ars'),
          HarvestManUrlParser('http://www.fylkesmannen.no/../fmt_hoved.asp',baseurl='http://www.fylkesmannen.no/osloogakershu')]          
    

    for hu in l:
        print 'Full filename = ', hu.get_full_filename()
        print 'Valid filename = ', hu.validfilename
        print 'Local Filename  = ', hu.get_filename()
        print 'Is relative path = ', hu.is_relative_path()
        print 'Full domain = ', hu.get_full_domain()
        print 'Domain      = ', hu.domain
        print 'Local Url directory = ', hu.get_url_directory_sans_domain()
        print 'Absolute Url = ', hu.get_full_url()
        print 'Absolute Url Without Port = ', hu.get_full_url_sans_port()
        print 'Local Directory = ', hu.get_local_directory()
        print 'Is filename parsed = ', hu.filelike
        print 'Path rel to domain = ', hu.get_relative_url()
        print 'Connection Port = ', hu.get_port_number()
        print 'Domain with port = ', hu.get_full_domain_with_port()
        print 'Relative filename = ', hu.get_relative_filename()
        print 'Anchor url     = ', hu.get_anchor_url()
        print 'Anchor tag     = ', hu.get_anchor()
        print
        

