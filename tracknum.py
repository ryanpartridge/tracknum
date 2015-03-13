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

import sys, os.path, string, re, subprocess
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

  return parser.parse_args()

def validateArgs():
  if not arguments.m4aFile:
    print >> sys.stderr, 'incorrect parameters -h for help'
    sys.exit()

  if not os.path.isfile(arguments.m4aFile):
    print >> sys.stderr, "ERROR: '" + arguments.m4aFile + "' does not exist"
    sys.exit()

  if arguments.m4aFile[-4:] != ".m4a":
    print >> sys.stderr, "ERROR: '" + arguments.m4aFile + "' is not an m4a file"
    sys.exit()

def readFileTags():
  try:
    output = subprocess.check_output(['/usr/bin/mp4info', arguments.m4aFile])
  except subprocess.CalledProcessError as e:
    print >> sys.stderr, "ERROR: couldn't read mp4 tags"
    sys.exit()

  lines = string.split(output, "\n")
  for line in lines:
    print "line: " + line 
  return ("", "")

def parseTrackFile():
  tf = open(arguments.trackFile)
  currentAlbum = '';
  titlePattern = re.compile(r"^\d\d\s+-\s+(.*)$")
  for line in tf.readlines():
    line = string.strip(line)
    if line == "" and currentAlbum:
      currentAlbum = ''
    else:
      if currentAlbum:
        matches = titlePattern.match(line)
        if (matches != None):
          title = matches.group(1)
          albums[currentAlbum].append(title)
      else:
        currentAlbum = line
        albums[currentAlbum] = []

  tf.close()

def writeAlbums():
  albumNames = albums.keys()
  albumNames.sort()
  for album in albumNames:
    if arguments.albumDir[-1] == os.sep:
      albumPath = arguments.albumDir + album
    else:
      albumPath = arguments.albumDir + os.sep + album
    if not os.path.isdir(albumPath):
      print "WARNING: '" + albumPath + "' does not exist or is not a directory -- skipping"
    else:
      print "Processing '" + album + "'..."
      index = 0;
      tracks = albums[album]
      trackFiles = os.listdir(albumPath)
      trackFiles.sort();
      for trackFile in trackFiles:
#        print "  " + trackFile + " --> " + tracks[index]
        command = '/usr/bin/eyeD3 -t "' + tracks[index] + '" "' + albumPath + os.sep + trackFile + '"'
#        print "  " + command
        os.system(command)
        index += 1
      command = '/usr/bin/eyeD3 --rename="%n - %t" "' + albumPath + '"'
#      print "  " + command
      os.system(command)
      print

def printAlbums():
  albumNames = albums.keys()
  albumNames.sort()
  for album in albumNames:
    print album
    for track in albums[album]:
      print '  ' + track
    print

if __name__ == "__main__":
  albums = {};
  arguments = parseArgs()
  validateArgs()
  (trackName, trackNum) = readFileTags()
  print "name: " + trackName + " (" + trackNum + ")"
  #parseTrackFile()
#writeAlbums()
