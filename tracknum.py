#! /usr/bin/python

'''
tracknum -- Custom Update Builder

track num renames M4A files according to the track number

It defines classes_and_methods

@author:     Ryan Partridge

@copyright:  2015 All rights reserved.

@license:    proprietary

@contact:    ryan.partridge@gmail.com
@deffield    updated: Updated
'''

import sys
import os.path
import string
import re
import subprocess
import shutil
from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter

__all__ = []
__version__ = 0.1
__date__ = '2015-03-12'
__updated__ = '2015-03-12'

program_name = os.path.basename(sys.argv[0])
program_version = "v%s" % __version__
program_build_date = str(__updated__)
program_version_message = '%%(prog)s %s (%s)' % (program_version, program_build_date)
program_shortdesc = __import__('__main__').__doc__.split("\n")[1]
program_license = '''%s

''' % (program_shortdesc)

def parseArgs():
  # Setup argument parser
  parser = ArgumentParser(description = program_license, formatter_class = RawDescriptionHelpFormatter)
  parser.add_argument('m4aFile', help = "M4A file to rename")
  parser.add_argument("dstDir", help = "Destination directory")

  return parser.parse_args()

def validateArgs():
  # is the file specified?
  if not arguments.m4aFile:
    print >> sys.stderr, "ERROR: must specify an M4A file"
    sys.exit()

  # does the file exist?
  if not os.path.isfile(arguments.m4aFile):
    print >> sys.stderr, "ERROR: '" + arguments.m4aFile + "' does not exist"
    sys.exit()

  # does the file end in .m4a?
  if arguments.m4aFile[-4:] != ".m4a":
    print >> sys.stderr, "ERROR: '" + arguments.m4aFile + "' is not an m4a file"
    sys.exit()

  # is the directory specified?
  if not arguments.dstDir:
    print >> sys.stderr, "ERROR: must specify a destination directory"
    sys.exit()

  # create the directory if it doesn't exist
  if not os.path.exists(arguments.dstDir):
    os.makedirs(arguments.dstDir)

  # does the location exist but it's not a directory?
  elif not os.path.isdir(arguments.dstDir):
    print >> sys.stderr, "ERROR: '" + arguments.dstDir + "' exists but is not a directory"
    sys.exit()

def readFileTags():
  title = ""
  track = 0
  trackTotal = 0
  try:
    output = subprocess.check_output(['/usr/bin/mp4info', arguments.m4aFile])
  except subprocess.CalledProcessError as e:
    print >> sys.stderr, "ERROR: couldn't read mp4 tags"
    sys.exit()

  titlePattern = re.compile(r"^\s+Name:\s+(.+)$")
  trackPattern = re.compile(r"^\s+Track:\s+(\d+)\s+of\s+(\d+).*$")

  lines = string.split(output, "\n")
  for line in lines:
    matches = titlePattern.match(line)
    if (matches != None):
      title = matches.group(1)
      print "Track title: " + title
      continue

    matches = trackPattern.match(line)
    if (matches != None):
      track = int(matches.group(1))
      trackTotal = int(matches.group(2))
      print "Track number: " + str(track) + " of " + str(trackTotal)
      continue

  return (title, track, trackTotal)

def copyTrackFile():
  (trackName, trackNum, trackTotal) = readFileTags()
  trackFileName = ""
  if (trackTotal > 99 and trackNum < 100):
      trackFileName = "0"
  trackFileName = trackFileName + str(trackNum) + " " + trackName + ".m4a"
  print "Old track name: " + os.path.basename(arguments.m4aFile)
  print "New track name: " + trackFileName
  outPath = os.path.join(arguments.dstDir, trackFileName)
  print "New destination: " + outPath
  shutil.copyfile(arguments.m4aFile, outPath)
  st = os.stat(arguments.m4aFile)
  if hasattr(os, 'utime'):
    os.utime(outPath, (st.st_atime, st.st_mtime))

if __name__ == "__main__":
  arguments = parseArgs()
  validateArgs()
  copyTrackFile()
