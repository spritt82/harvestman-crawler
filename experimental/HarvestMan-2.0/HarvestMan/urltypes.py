# -- coding: latin-1
"""
urltypes - Module defining types of URLs and their
relationships.

This module is part of the HarvestMan program.
For licensing information see the file LICENSE.txt that
is included in this distribution.

Author: Anand B Pillai <anand at harvestmanontheweb.com>

Created Anand B Pillai April 18 2007

Copyright (C) 2007, Anand B Pillai.
"""

__version__ = '2.0 b1'
__author__ = 'Anand B Pillai'

# The URL types are defined as classes with easy-to-use
# string representations. However the class names are
# unlike regular HarvestMan class names (which usually start
# with 'HarvestMan'). Instead they are capitalized and start
# with TYPE_.

# Also, these classes are to be used as "raw", in other words
# ideally the clients of these classes need not create instances
# from the classes. Instead they should use them as given,
# i.e as classes.

class TYPE_META(type):
    """ Meta-class for type classes """

    def __eq__(cls, other):
        return (str(cls) == str(other))

    def __str__(cls):
        return cls.typ

    def isA(cls, baseklass):
        """ Check whether the passed class is a subclass of my class """
        
        return issubclass(cls, baseklass)

class TYPE_ANY(str):
    """ Class representing a URL which belongs to any type.
    This is the base class for all other URL types """

    __metaclass__ = TYPE_META
    
    typ = 'generic'

class TYPE_NONE(TYPE_ANY):
    """ Class representing the None type for URLs """

    __metaclass__ = TYPE_META

    typ = 'none'
    
class TYPE_WEBPAGE(TYPE_ANY):
    """ Class representing a webpage URL. A webpage URL will
    consist of some (X)HTML markup which can be parsed by an
    (X)HTML parser. """

    typ = 'webpage'

class TYPE_BASE(TYPE_WEBPAGE):
    """ Class representing the base URL of a web site. This is
    a special kind of webpage type """

    typ = 'base'

class TYPE_ANCHOR(TYPE_WEBPAGE):
    """ Class representing HTML anchor links. Anchor links are
    part of the same web-page and are typically labels defined
    in the same page or in another page. They start with a '#'"""

    typ = 'anchor'

class TYPE_FRAMESET(TYPE_WEBPAGE):
    """ Class representing a URL which defines HTML frames. The
    children of this URL point to HTML frame documents """

    typ = 'frameset'


class TYPE_FRAME(TYPE_WEBPAGE):
    """ Class representing a URL which acts as the source for an
    HTML 'frame' element. This URL is typically the child of
    an HTML 'frameset' URL """

    typ = 'frame'
    
class TYPE_QUERY(TYPE_ANY):
    """ Class representing a URL which is used to submit queries to
    web servers. Such queries can result in html or non-html result,
    but typically they consist of session IDs """

    typ = 'query'
    
class TYPE_FORM(TYPE_QUERY):
    """ A URL which points to an action, usually used to submit
    form contents to a ReST endpoint. This URL is part of the submit
    action of an HTML <form> element """

    typ = 'form'

class TYPE_IMAGE(TYPE_ANY):
    """ Class representing a URL which points to a binary raster image """

    typ = 'image'

class TYPE_STYLESHEET(TYPE_ANY):
    """ Class representing a URL which points to a stylesheet (CSS) file """

    typ = 'stylesheet'

class TYPE_JAVASCRIPT(TYPE_ANY):
    """ Class which defines a URL which stands for server-side javascript files """

    typ = 'javascript'

class TYPE_JAPPLET(TYPE_ANY):
    """ Class which defines a URL that points to a Java applet class """

    typ = 'javaapplet'

class TYPE_JAPPLET_CODEBASE(TYPE_ANY):
    """ Class which defines a URL that points to the code-base path of a Java applet """

    typ = 'appletcodebase'
    
class TYPE_FILE(TYPE_ANY):
    """ Class representing a URL which points to any kind of file other
    than webpages, images, stylesheets,server-side javascript files, java
    applets, form queries etc """

    # This is a generic catch-all for all URLs which are not defined so far.
    typ = 'file'

class TYPE_DOCUMENT(TYPE_ANY):
    """ Class which stands for URLs that point to documents which can be
    indexed by search engines. Examples are text files, xml files, PDF files,
    word documents, open office documents etc """

    # This type is not used in HarvestMan, but is useful for indexers
    # which work with HarvestMan, such as swish-e.
    typ = 'document'


# An easy-to-use dictionary for type string to type class mapping

type_map = { 'generic' : TYPE_ANY,
             'webpage' : TYPE_WEBPAGE,
             'base': TYPE_BASE,
             'anchor': TYPE_ANCHOR,
             'query': TYPE_QUERY,
             'form' : TYPE_FORM,
             'image': TYPE_IMAGE,
             'stylesheet': TYPE_STYLESHEET,
             'javascript': TYPE_JAVASCRIPT,
             'javaapplet': TYPE_JAPPLET,
             'appletcodebase': TYPE_JAPPLET_CODEBASE,
             'file': TYPE_FILE,
             'document': TYPE_DOCUMENT }


def getTypeClass(typename):
    """ Return the type class, given the type name """

    return type_map.get(typename, TYPE_ANY)

if __name__ == "__main__":
    print TYPE_ANY == 'generic'
    print TYPE_WEBPAGE == 'webpage'
    print TYPE_BASE == 'base'
    print TYPE_ANCHOR == 'anchor'
    print TYPE_QUERY == 'query'
    print TYPE_FORM == 'form'
    print TYPE_IMAGE == 'image'
    print TYPE_STYLESHEET == 'stylesheet'
    print TYPE_JAVASCRIPT == 'javascript'
    print TYPE_JAPPLET == 'javaapplet'
    print TYPE_JAPPLET_CODEBASE == 'appletcodebase'
    print TYPE_FILE == 'file'
    print TYPE_DOCUMENT == 'document'
    

    print TYPE_ANY in ('generic','webpage')
    print issubclass(TYPE_ANCHOR, TYPE_WEBPAGE)
    print issubclass(TYPE_BASE, TYPE_WEBPAGE)    
    print type(TYPE_ANCHOR), type(TYPE_ANY)
    
    print TYPE_ANCHOR.isA(TYPE_WEBPAGE)
    print TYPE_ANCHOR.isA(TYPE_ANY)
    print TYPE_IMAGE.isA(TYPE_WEBPAGE)
    print TYPE_ANY.isA(TYPE_ANY)
    print TYPE_IMAGE in ('image','stylesheet')
