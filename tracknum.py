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
  parser.add_argument('srcDir', help = "Source directory")
  parser.add_argument("dstDir", help = "Destination directory")
  parser.add_argument("-t", "--set-track", action="store_true", dest="setTrack", help = "Set the track number tag", default = False)

  return parser.parse_args()

def validateArgs():
  # is the source directory specified?
  if not arguments.srcDir:
    print >> sys.stderr, "ERROR: must specify a source directory"
    sys.exit()

  # does the file exist?
  if not os.path.isdir(arguments.srcDir):
    print >> sys.stderr, "ERROR: '" + arguments.srcDir + "' does not exist or is not a directory"
    sys.exit()

  # is the output directory specified?
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

def setTrackNumTag(trackFile, number):
  try:
    output = subprocess.check_output(['/usr/bin/mp4tags', '-t', str(number), trackFile])
  except subprocess.CalledProcessError as e:
    print >> sys.stderr, "ERROR: couldn't set the mp4 tag on file:" + trackFile
    sys.exit()

def readFileTags(trackFile):
  title = ""
  track = 0
  trackTotal = 0
  try:
    output = subprocess.check_output(['/usr/bin/mp4info', trackFile])
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

def copyTrackFile(trackSrcFile, forceTrackNum = 0):
  (trackName, trackNum, trackTotal) = readFileTags(trackSrcFile)
  trackFileName = ""
  if forceTrackNum > 0:
      trackNum = forceTrackNum
  if trackTotal > 9 and trackNum < 10:
      trackFileName += "0"
  if trackTotal > 99 and trackNum < 100:
      trackFileName += "0"
  trackFileName += str(trackNum) + " " + trackName + ".m4a"

  print "Old track name: " + os.path.basename(trackSrcFile)
  print "New track name: " + trackFileName

  trackDstFile = os.path.join(arguments.dstDir, trackFileName)
  print "New destination: " + trackDstFile 

  shutil.copyfile(trackSrcFile, trackDstFile)
  st = os.stat(trackSrcFile)
  if hasattr(os, 'utime'):
    os.utime(trackDstFile, (st.st_atime, st.st_mtime))

  if forceTrackNum > 0:
    print "Resetting track number to: " + str(count)
    setTrackNumTag(trackDstFile, count)
  print

if __name__ == "__main__":
  arguments = parseArgs()
  validateArgs()
  rawFiles = os.listdir(arguments.srcDir)
  rawFiles.sort()
  files = []

  # need an accurate count -- only keep .m4a files
  for f in rawFiles:
    filePath = os.path.join(arguments.srcDir, f)
    if not f.startswith(".") and f.endswith(".m4a") and os.path.isfile(filePath):
      files.append(f)

  count = 1;
  for f in files:
    filePath = os.path.join(arguments.srcDir, f)
    #print "File name: " + filePath
    forceTrackNum = 0
    if arguments.setTrack:
      forceTrackNum = count
    copyTrackFile(filePath, forceTrackNum)
    count += 1

