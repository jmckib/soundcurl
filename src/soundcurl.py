#!/usr/bin/env python
from HTMLParser import HTMLParser
import json
import shutil
from StringIO import StringIO
import sys
import traceback
import urllib2

from bs4 import BeautifulSoup
from mutagen.id3 import ID3, APIC, TIT2, TPE1

unescape_html = HTMLParser().unescape


def main():
    try:
        if len(sys.argv) != 2:
            raise ValueError('Expecting one argument, the URL of a song on SoundCloud.')

        sound_cloud_page = SoundCloudPage(sys.argv[1])
        sound_cloud_page.download_song()
    except:
        traceback.print_exception(*sys.exc_info())
        print ('\nSorry, you just experienced an error :(\nPlease it '
               'to me here: https://github.com/jmckib/soundcurl/issues/new')


class SoundCloudPage(object):

    def __init__(self, page_url):
        # Http GET parameters screw up the expected format of the page
        # sometimes. Example: `?fb_action_ids` from soundcloud links on
        # facebook.
        self._page_url = page_url.split('?')[0]
        # Use StringIO so we can consume the response multiple times.
        self._http_response = StringIO(urllib2.urlopen(self._page_url).read())

    def download_song(self):
        """Download song from given SoundCloud URL and write to disk as mp3.

        The URL must be for a single song, not a set or an artist's page.

        Title, artist, and cover art metadata are included in the mp3.
        """
        stream_url_line = self._get_stream_url_line()
        if not stream_url_line:
            raise ValueError(
                "Can't find stream URL. Are you sure '%s' is the url of a "
                "song on SoundCloud?" % self._page_url)

        stream_data = self._get_stream_data(stream_url_line)
        # A file-like object containing the song data.
        song = urllib2.urlopen(stream_data['streamUrl'])

        # Write the song to disk.
        song_title, artist = self._get_title_and_artist(stream_data)
        # Believe it or not, there are songs with forward slahes in their
        # titles, but we can't use that as a file name.
        song_filename = '%s.mp3' % song_title.replace('/', '|')
        print "Writing '%s'" % song_filename
        shutil.copyfileobj(song, open(song_filename, 'wb'))

        print 'Writing song metadata...'
        tags = ID3()
        tags.add(TIT2(encoding=3, text=song_title))  # Song title
        print "\ttitle: '%s'" % song_title
        tags.add(TPE1(encoding=3, text=artist))  # Artist
        print "\tartist: '%s'" % artist

        # Add track artwork.
        # First, get a URL for the artwork as a jpeg.
        soup = BeautifulSoup(self._get_fresh_http_response())
        artwork_img = soup.find('img', alt="Track artwork")
        artwork_url = artwork_img.get('src') if artwork_img else None

        if not artwork_url:
            print 'Failed to find artwork URL.'
        else:
            print 'Writing cover art...'
            artwork = urllib2.urlopen(artwork_url)
            tags.add(APIC(
                encoding=3, mime='image/jpeg', desc=u'',
                type=3,  # indicates that this is the front cover art
                data=artwork.read())
            )
        tags.save(song_filename)

    def _get_fresh_http_response(self):
        self._http_response.seek(0)
        return self._http_response

    def _get_stream_url_lines(self):
        """Return an iterator of the stream url lines in the http response.

        A "stream url line" is a line of javascript code in the page's html
        that contains the url of an mp3. The stream url lines are in the same
        order as the songs on the page.
        """
        return (line for line in self._get_fresh_http_response()
                if 'http://media.soundcloud.com/stream/' in line)

    def _get_stream_url_line(self):
        """Return the first line in the http response with a stream url in it.

        If there are no stream urls, return None. See `_get_stream_url_lines`
        for more explanation.
        """
        return next(self._get_stream_url_lines(), None)

    def _get_stream_data(self, stream_url_line):
        """Return dictionary of stream data from a stream url line."""
        # stream_url_line looks something like this
        # window.SC.bufferTracks.push(<BIG_JAVASCRIPT_DICT>);\n
        # Since a javascript dict is really a json dict, we decode it as one.
        return json.loads(stream_url_line[28:-3])

    def _get_all_stream_data(self):
        return (self._get_stream_data(stream_url_line) for stream_url_line
                in self._get_stream_url_lines())

    def _get_title_and_artist(self, stream_data):
        try:
            artist, title = stream_data['title'].split(' - ')
        except ValueError:
            artist = stream_data['user']['username']
            title = stream_data['title']
        return unescape_html(title).strip(), unescape_html(artist).strip()

if __name__ == '__main__':
    main()
