from setuptools import setup

setup(
    name='soundcurl',
    version='0.1.0',
    description='A command line utility for downloading songs from SoundCloud.',
    author='Jeremy McKibben-Sanders',
    author_email='jmckib2+soundcurl@gmail.com',
    url='https://github.com/jmckib/soundcurl',
    package_dir={'': 'src'},
    py_modules=['soundcurl'],
    entry_points={'console_scripts': ['soundcurl = soundcurl:main']},
    install_requires=['beautifulsoup4==4.2.1', 'mutagen==1.21'],
)
