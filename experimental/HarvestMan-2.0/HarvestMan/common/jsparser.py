""" jsparser - Basic HTML parser which extracts valid Javascript
statements embedded between <script>...</script> tags. The parser
takes care of comment processing and closely follows the behaviour
of Firefox. 

This module is part of the HarvestMan program. For licensing
information see the file LICENSE.txt that is included in this
distribution.

Created Anand B Pillai <anand at harvestmanontheweb.com> Aug 31 2007

Copyright (C) 2007 Anand B Pillai.

"""

import re

scriptstartre = re.compile(r'(\<script\s*[a-zA-Z]*\=*[\"a-zA-Z\/]*\>)', re.IGNORECASE|re.UNICODE)
scriptendre = re.compile(r'(\</script\>)', re.IGNORECASE|re.UNICODE)
jscommentopenre = re.compile(r'\<\!--')
jscommentclosere = re.compile(r'\/\/--\>')
syntaxendre = re.compile(r';$')

class JSParser(object):
   """ Javascript parser which extracts javascript statements
   embedded in HTML. The parser only performs extraction, and no
   Javascript tokenizing """

   # The name of this class is a misnomer since it actually
   # only parses HTML to extract Javascript; it does not do any
   # Javascript parsing apart from processing comments.
   
   def __init__(self):
       self.reset()

   def reset(self):
       self.rawdata = ''
       self.buffer = ''
       self.statements = []
       
   # Currently only does a match of site redirection
   # javascript using regular expressions
   def feed(self, data):
       self.rawdata = self.rawdata + data
       # Extract all content between <script>...</script> tags
       self.goahead()
       # Process extracted statements
       self.process()
       pass
    
   # Internal - parse the HTML to extract Javascript
   def goahead(self):

       rawdata = self.rawdata
       flag = False
       
       # This scans the HTML for javascript statements
       # At the end of parsing, all statements are appended
       # to the list of statements.
       while rawdata:
          
          match1 = scriptstartre.match(rawdata)
          match2 = scriptendre.match(rawdata)

          if match1:
             # If the following line is uncommented, JS statements
             # without the closing </script> tag will not be added
             # to the list of statements. However if it is commented
             # out, such statements will be added along withe the
             # set of statements in the next <script>...</script>
             # section. The preferred behaviour is the former.
             self.buffer = ''
             i = match1.end()
             rawdata = rawdata[i:]
             flag = True
          elif match2:
             i = match2.end()
             rawdata = rawdata[i:]
             self.statements.append(self.buffer.strip())
             self.buffer = ''
             flag = False

          if flag:
             if rawdata:
                self.buffer += rawdata[0]
                rawdata = rawdata[1:]
          elif not match2:
             rawdata = rawdata[1:]

   # Internal - strip comments etc from javascript
   def process(self):

      # If the JS is embedded in HTML comments <!--- js //-->
      # remove the comments. This logic takes care of trimming
      # any junk before/after the comments modeling the
      # behaviour of a browser (Firefox) as closely as possible.
      
      flag  = True
      for x in range(len(self.statements)):
         s = self.statements[x]
         
         m = jscommentopenre.search(s)
         if m:
            # If there is junk before the comment, then the JS does not
            # work in Firefox. We are following the same behaviour.
            if m.start() == 0: 
               # Trim statement before start of comment
               s = s[m.end():]
               flag = False
               m = jscommentclosere.search(s)
               if m:
                  # Firefox does not seem to care if there is junk after
                  # comment closing and before </script> closing tag. We
                  # are following the same behaviour.
                  
                  # Trip statement upto end of comment
                  s = s[:m.start()]
                  flag = True
            else:
               flag = False

         # Clean up any syntax end chars
         s = syntaxendre.sub('', s).strip()
         
         if flag:
            self.statements[x] = s
         else:
            self.statements[x] = ''

      # Trim any empty statements
      self.statements = [s for s in self.statements if s]
      
if __name__ == "__main__":
    p =  JSParser()
    data = """<html> <title>Struer Kommune - Kommunen</title> <body bgcolor="#FFFFFF">
    <script language="javascript">  <!--
    location.href =   "http://www.struer.dk/webtop/site.asp?site=5";
    //--> crap
    </script>
    </body> </html>"""

    p.feed(data)
    print p.statements
    

    


