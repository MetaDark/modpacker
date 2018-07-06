#!/usr/bin/env python3

"""modpacker

Usage:
  modpacker install <modpack> [<directory>]

Options:
  -h --help     Show this screen.
  --version     Show version.
"""

from base import Mod, Repo
from docopt import docopt
from source.curseforge import CurseForge
from source.micdoodle8 import Micdoodle8
from source.optifine import OptiFine
from source.pixelmon_reforged import PixelmonReforged
from typing import Set
from url import Url
import cgi
import os
import requests
import url as urllib

version = '1.0'
sources = {
    'micdoodle8.com': Micdoodle8(),
    'minecraft.curseforge.com': CurseForge(),
    'optifine.net': OptiFine(),
    'reforged.gg': PixelmonReforged(),
}

def main(args=None) -> None:
    args = docopt(__doc__, version=version, argv=args)
    modpack = args['<modpack>']
    directory = args['<directory>']
    if directory is None:
        directory = './'

    install_modpack(modpack, directory)

def install_modpack(modpack: os.PathLike, directory: os.PathLike) -> None:
    with open(modpack, 'r') as f:
        app, version = next(f).split()
        if app != 'minecraft':
            raise LookupError('unsupported application: {}'.format(app))

        # Get links to lastest versions of mods
        downloaded: Set[Url] = set()
        for line in f:
            line = line.strip()
            print('Finding lastest version of {}'.format(line))
            source_id, *args = line.split()
            source = sources[source_id]

            if isinstance(source, Repo):
                mod = source.mod(args[0])
            elif isinstance(source, Mod):
                mod = source

            for url in mod.latest(version):
                print('Found {}'.format(url))
                if url in downloaded:
                    print('Already downloaded: {}'.format(url))
                else:
                    print('Downloading: {}'.format(url))
                    download(url, directory)
                    downloaded.add(url)

            print()

def download(url: Url, directory: os.PathLike) -> None:
    res = requests.get(url)

    try:
        filename = cgi.parse_header(res.headers['Content-Disposition'])[1]['filename']
    except:
        filename = urllib.filename(Url(res.url))

    path = os.path.join(directory, filename)
    open(path, 'wb').write(res.content)

if __name__ == '__main__':
    main()
