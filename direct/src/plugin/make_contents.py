#! /usr/bin/env python

"""
This command will build the contents.xml file at the top of a Panda3D
download hierarchy.  This file lists all of the packages hosted here,
along with their current versions.

This program runs on a local copy of the hosting directory hierarchy;
it must be a complete copy to generate a complete contents.xml file.

make_contents.py [opts]

Options:

  -d stage_dir

     Specify the staging directory.  This is a temporary directory on
     the local machine that contains a copy of the web server
     contents.  The default is the current directory.

"""

import sys
import getopt
import os

import direct
from pandac.PandaModules import *

from FileSpec import FileSpec

class ArgumentError(AttributeError):
    pass

class ContentsMaker:
    def __init__(self):
        self.stageDir = None

    def build(self):
        if not self.stageDir:
            raise ArgumentError, "Stage directory not specified."

        self.packages = []
        self.scanDirectory()

        if not self.packages:
            raise ArgumentError, "No packages found."

        # Now write the contents.xml file.
        contentsFileBasename = 'contents.xml'
        contentsFilePathname = Filename(self.stageDir, contentsFileBasename)

        f = open(contentsFilePathname.toOsSpecific(), 'w')
        print >> f, '<?xml version="1.0" ?>'
        print >> f, ''
        for packageName, packageVersion, packagePlatform, file in self.packages:
            print >> f, '<package name="%s" version="%s" platform="%s" %s />' % (
                packageName, packageVersion, packagePlatform or '', file.getParams())
        f.close()

    def scanDirectory(self):
        """ Walks through all the files in the stage directory and
        looks for the package directory xml files. """

        startDir = self.stageDir.toOsSpecific()
        if startDir.endswith(os.sep):
            startDir = startDir[:-1]
        prefix = startDir + os.sep
        for dirpath, dirnames, filenames in os.walk(startDir):
            if dirpath == startDir:
                localpath = ''
                xml = ''
            else:
                assert dirpath.startswith(prefix)
                localpath = dirpath[len(prefix):].replace(os.sep, '/') + '/'
                xml = dirpath[len(prefix):].replace(os.sep, '_') + '.xml'

            if xml not in filenames:
                continue
            
            if xml.count('_') == 1:
                basename = xml.split('.')[0]
                packageName, packageVersion = basename.split('_')
                packagePlatform = None
                file = FileSpec(localpath + xml,
                                Filename(self.stageDir, localpath + xml))
                print file.filename
                self.packages.append((packageName, packageVersion, packagePlatform, file))

            if xml.count('_') == 2:
                basename = xml.split('.')[0]
                packageName, packageVersion, packagePlatform = basename.split('_')
                file = FileSpec(localpath + xml,
                                Filename(self.stageDir, localpath + xml))
                print file.filename
                self.packages.append((packageName, packageVersion, packagePlatform, file))
        
                
def makeContents(args):
    opts, args = getopt.getopt(args, 'd:h')

    cm = ContentsMaker()
    cm.stageDir = Filename('.')
    for option, value in opts:
        if option == '-d':
            cm.stageDir = Filename.fromOsSpecific(value)
            
        elif option == '-h':
            print __doc__
            sys.exit(1)

    cm.build()
        

if __name__ == '__main__':
    try:
        makeContents(sys.argv[1:])
    except ArgumentError, e:
        print e.args[0]
        sys.exit(1)