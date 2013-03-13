#!/usr/bin/python
#
# checkPlease.py: Downloads all songs and metadata from google music
#

import json
import getpass
from gmusicapi import Api
import os
import signal
import sys
import time
import urllib2

BASEDIR = "./google_music-" + str(time.strftime("%Y-%m-%d_%H%M%S"))
SONG_METADATA = 'all_songs.json'
PLAYLIST_METADATA = 'all_playlists.json'

def abort(signal, frame):
    print "\nExiting."
    sys.exit(signal)

def login(api, email, password):
    if not api.login(email, password) or api.session.is_authenticated == False:
        print "Login failed."
    else:
        print "Logged in."
    

def main():
    """
    Main stuff
    """
    # Catch ^C
    signal.signal(signal.SIGINT, abort)

    # Create our API instance
    api = Api()

    # Get e-mail address
    if 'GMUSIC_ADDRESS' in os.environ:
        email = os.environ['GMUSIC_ADDRESS']
        print "Detected Google Music Address: %s" % email
    else:
        email = ''
        while not validate_email(email):
            email = raw_input('Google Music E-mail Address: ')

    # Read password from user
    password = getpass.getpass()
    login(api, email, password)

    # Setup output directory
    if not os.path.exists(BASEDIR):
        try:
            os.mkdir(BASEDIR)
        except Exception, e:
            print "Unable to create directory %s." % BASEDIR
            os.exit(1)

    # Get song and track metadata
    all_songs = api.get_all_songs()
    filename = os.path.join(BASEDIR, SONG_METADATA)
    print "Writing song metadata to %s" % filename
    open(filename, 'w').write(json.dumps(all_songs))

    all_playlists = [ api.get_playlist_songs(playlist)
                    for playlist in api.get_all_playlist_ids() ]

    filename = os.path.join(BASEDIR, PLAYLIST_METADATA)
    print "Writing playlist metadata to %s" % filename
    open(filename, 'w').write(json.dumps(all_playlists))

    print "Fetching songs..."
    for song in all_songs:
        song_url = api.get_song_download_info(song['id'])[0]
        song_filename = urllib2.quote("%(artist)s-%(album)s-%(track)s-%(title)s.mp3" % \
                        song).replace('%20', '_')
        song_path = os.path.join(BASEDIR, song_filename)
        print "Saving: %s" % song_filename
        with open(song_path, 'w') as f:
            f.write(urllib2.urlopen(song_url).read())


def validate_email(email):
    if not '@' in email and len(email) < 6:
        return False
    return True

if __name__ == '__main__':
    main()
