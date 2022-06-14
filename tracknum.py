#! /usr/bin/python3

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
import shutil
import taglib
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
  parser = ArgumentParser(description = program_license)
  parser.add_argument('srcDir', help = "Source directory")
  parser.add_argument("dstDir", help = "Destination directory")
  parser.add_argument("-n", "--track-num", dest="startTrackNum", type=int, help = "Start tracks at this number", default = 1)

  return parser.parse_args()

def validateArgs():
  # is the source directory specified?
  if not arguments.srcDir:
    print("ERROR: must specify a source directory", file=sys.stderr)
    sys.exit()

  # does the file exist?
  if not os.path.isdir(arguments.srcDir):
    print("ERROR: '{}' does not exist or is not a directory".format(arguments.srcDir), file=sys.stderr)
    sys.exit()

  # is the output directory specified?
  if not arguments.dstDir:
    print("ERROR: must specify a destination directory", file=sys.stderr)
    sys.exit()

  # create the directory if it doesn't exist
  if not os.path.exists(arguments.dstDir):
    os.makedirs(arguments.dstDir)

  # does the location exist but it's not a directory?
  elif not os.path.isdir(arguments.dstDir):
    print("ERROR: '{}' exists but is not a directory".format(arguments.dstDir), file=sys.stderr)
    sys.exit()

  # validate the track number
  if arguments.startTrackNum < 1:
    print("ERROR: track number must be 1 or greater", file=sys.stderr)
    sys.exit()

def setTrackNumTag(trackFile, number, total):
  try:
    song = taglib.File(trackFile)
    song.tags["TRACKNUMBER"] = ["{}/{}".format(number, total)]
    song.save()
  except:
    print("ERROR: couuldn't set the mp4 tag on file: {}".format(trackFile))
    sys.exit()

def readFileTags(trackFile):
  title = ""
  track = 0
  trackTotal = 0
  try:
    song = taglib.File(trackFile)
  except OSError as e:
    print("ERROR: couuldn't read mp4 tags from {}".format(trackFile), file=sys.stderr)
    sys.exit()

  if "TITLE" in song.tags:
    title = song.tags["TITLE"][0]
    print("Track title: {}".format(title))

  if "TRACKNUMBER" in song.tags:
    trackNumText = song.tags["TRACKNUMBER"][0]
    parts = trackNumText.split('/')
    if len(parts) == 2:
      track = int(parts[0])
      trackTotal = int(parts[1])
      print("Track number: {} of {}".format(track, trackTotal))

  return (title, track, trackTotal)

def copyTrackFile(trackSrcFile, startTrackNum = 1):
  (trackName, trackNum, trackTotal) = readFileTags(trackSrcFile)

  trackFileName = ""
  if startTrackNum > 1:
      trackNum = startTrackNum
  if trackTotal > 9 and trackNum < 10:
      trackFileName += "0"
  if trackTotal > 99 and trackNum < 100:
      trackFileName += "0"
  trackFileName += str(trackNum) + " " + trackName + ".m4a"

  print("Old track name: {}".format(os.path.basename(trackSrcFile)))
  print("New track name: {}".format(trackFileName))

  trackDstFile = os.path.join(arguments.dstDir, trackFileName)
  print("New destination: {}".format(trackDstFile))

  shutil.copyfile(trackSrcFile, trackDstFile)
  st = os.stat(trackSrcFile)
  if hasattr(os, 'utime'):
    os.utime(trackDstFile, (st.st_atime, st.st_mtime))

  if startTrackNum > 0:
    print("Resetting track number to: {}".format(trackNum))
    setTrackNumTag(trackDstFile, trackNum, trackTotal)
  print()

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

  count = 0;
  for f in files:
    filePath = os.path.join(arguments.srcDir, f)
    #print("File name: {}".format(filePath))
    startTrackNum = 1
    if arguments.startTrackNum > 1:
      startTrackNum = arguments.startTrackNum + count
    copyTrackFile(filePath, startTrackNum)
    count += 1

