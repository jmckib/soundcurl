soundcurl
=========

A command line tool for downloading songs from SoundCloud, including metadata and cover art!

Requires python2.6+

Usage
------

Provide a SoundCloud URL for a single song, and soundcurl will write the mp3 file in the current directory:
```
$: soundcurl https://soundcloud.com/odesza/we-were-young
Writing 'We Were Young.mp3'
Writing song metadata...
        title: 'We Were Young'
        artist: 'ODESZA'
Writing cover art...
```

Installation
------

```Shell
git clone git@github.com:jmckib/soundcurl.git
cd soundcurl
python setup.py install
```
