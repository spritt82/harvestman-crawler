*************************
*                       *
* HarvestMan Webcrawler *
*                       *
*************************

Introduction
------------

HARVESTMan is an internet offline crawler (robot) program written 
in python. It helps you to grab pages from the internet and store 
it in a local directory for offline browsing.

This is version 1.5 beta 1.

Author: Anand B Pillai.

Copyright: All software in this distribution is (C) Anand B Pillai.

License: See the file LICENSE.TXT.

WWW
---
http://harvestmanontheweb.com, http://harvestman.freezope.org

Getting started 
---------------

Unarchive the file to a directory of your choice. 

% tar -xjf HarvestMan-1.5-b1.tar.bz2

Change to directory 'HarvestMan-1.5-b1' and install
the program.

Installation steps are given below.

How to Install
--------------
Make sure you are at the top-level HarvestMan
directory. For this version it is 'HarvestMan-1.5-b1'.

On Windows, you need to run the setup.py script
to install the program. 

Open a Windows cmd shell and type the following.

% python setup.py build
% python setup.py install

On Linux/Unix, you can use the install script
named 'install'. This is a bash script. To run
it, first become the super-user by,

$ su

Then install using,

$ ./install

In Linux/Unix/Mac, it is a good idea to enable the
system wide symbolic link that will create a 
link to harvestman main module in the /usr/bin
directory as 'harvestman', so you can run the program
by typing 'harvestman' at a shell prompt.

The install script will work on Windows based Unix emulation
layers such as cygwin also.

Running the program
-------------------
        
The program require a configuration file to run. This
is named 'config.xml' by default. To pass a different
configuration file, use the command-line argument '-C'
or '--configfile'.

Create the config file by editing or by using the config 
file generation script provided in the 'tools' sub-directory
named 'genconfig.py'. You can also locate a sample config file
in the 'HarvestMan' directory.

If you prefer the online way, you can generate a configuration 
file by using the config generator by pointing your browser to the url, 
http://harvestman.freezope.org/templates/configgenerator. Make sure
to select the 'XML' option for the type of config file.

Windows
-------
You need to either set the PATH environment variable
to pick up the HarvestMan main module or run the program from its
installation directory. This is normally the sub-directory named
'HarvestMan' in the site-packges directory of your Python installation
folder.

Then in the command prompt,

% harvestman.py 

or

% python harvestman.py

Linux/Unix/Mac
--------------

If you have enabled the system-wide symbolic link,
you can run the program just by typing 'harvestman'
at the console.

$ harvestman

Otherwise, you have to create a symbolic link to
the file 'harvestman.py' in a directory of your choice
and run the program from that directory as,

$ python harvestman.py

This will start the program using the settings in the
config file. 

Command line mode
-----------------
HarvestMan supports command-line options.

To download a URL without crawling it, pass the -N or
--nocrawl option to the program along with the URL.

For example,

$ harvestman.py -N www.python.org

For information on the command line options, run the program 
with the --help or -h option.

For a complete FAQ on the command line options, visit
http://harvestman.freezope.org/commandline.html .

Project file mode
-----------------

HarvestMan writes a project file before it starts crawling websites.
This file has the extension '.hbp' and is written in the base 
directory of the project.

You can read this file back to restart the project later on. 

For this, use the --projectfile or '-P option and pass the project file
path as argument. This reruns a previously ran project.

The Config file
---------------

The config file provides the program with its settings.
It is an xml file with top-level elements and children.
Each top-level element denotes a section of HarvestMan
configuration. Each child element denotes either a minor
section or an actual configuration element.

Example:

      <project skip="0">
        <url>http://www.python.org/doc/current/tut/tut.html</url>
        <name>pytut</name>
        <basedir>D:/websites</basedir>
        <verbosity value="3"/>
      </project>

The new version of the config file separates config variables into
8 different sections(elements) as described below.

Section                       Description

1. project                    All project related variables
2. network                    All network related variables lik proxy,
                              proxy username/password etc.
3. download                   All download related variables (html/image/
                              stylesheets/cookies etc)
4. control                    All download control variables (filters/
                              maximum limits/timeouts/depths/robots.txt)
5. system                     Any system related variable( fastmode/thread status/
                              thread timeouts/thread pool size etc)
6. indexer                    All indexer related variables (localize etc)
7. files                      All harvestman file settings (config/message log/ 
                              error log/url list file etc) 
8.display                    Display (GUI/browser) related setting
  
HarvestMan accepts about 60 configuration options in total.

For a detailed discussion on the options, refer the HarvestMan 
documentation files in the 'doc' sub-directory or point your browser
to http://harvestman.freezope.org/configoptions.html .

A script genconfig.py is provided to generate a config file
based on inputs from the user. A script convertconfig.py
helps to convert configuration files between the new
XMl version and the older text version.

Platforms
---------

This HarvestMan version has been developed on Python 2.4, specifically
Python 2.4.1 .

It is preferred to run HarvestMan with the latest stable release of Python,
to get the benefits of all features and for optimal performance. 
Right now this is Python 2.4.3 .

The minimal requirement is any version of Python 2.3 .

HarvestMan should work on all platforms where Python is supported.
It has been specifically tested on Windows NT/2000, Redhat Linux 9.0,
Fedora Core 1,2,3,4, Ubuntu Hoary and Mandrake 10.1 .

This version has been developed partly on Ubuntu "Hoary Hedgehog"
and Windows 2000/XP, running Python 2.4.1 .

You can use the script check_dep.py to check dependencies for
your platform.

More Documentation
------------------
Read the HarvestMan documentation in the 'doc' sub-directory for
more information. More information is also available in the project
web page.

Changes & Fix History
---------------------    
See the file Changes.txt.

Change Log for this Version
---------------------------
See the file ChangeLog.txt.























    

    
    

