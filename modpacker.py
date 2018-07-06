#!/usr/bin/env python3

"""modpacker

Usage:
  modpacker.py <modpack>

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
import cgi
import os
import requests
import url as urllib

sources = {
    'micdoodle8.com': Micdoodle8(),
    'minecraft.curseforge.com': CurseForge(),
    'optifine.net': OptiFine(),
    'reforged.gg': PixelmonReforged(),
}

def download(url, directory):
    res = requests.get(mod)

    try:
        filename = cgi.parse_header(res.headers['Content-Disposition'])[1]['filename']
    except KeyError:
        filename = urllib.filename(res.url)

    path = os.path.join(directory, filename)
    open(path, 'wb').write(res.content)

if __name__ == '__main__':
    args = docopt(__doc__, version='modpacker 1.0')
    with open(args['<modpack>'], 'r') as modpack:
        app, version = next(modpack).split()
        if app != 'minecraft':
            raise LookupError('unsupported application: {}'.format(app))

        # Get links to lastest versions of mods
        mods = set()
        for mod in modpack:
            print('Finding lastest version of {}'.format(mod.strip()))
            source_id, *mod_id = mod.split()
            source = sources[source_id]

            if isinstance(source, Repo):
                source = source.mod(mod_id[0])

            urls = list(source.latest(version))
            for url in urls:
                print('Found {}'.format(url))

            mods.update(urls)

        # Create mods directory if it doesn't exist
        try:
            os.mkdir('mods')
        except FileExistsError:
            pass

        # Download mods
        for mod in mods:
            print('Downloading {}'.format(mod))
            download(mod, 'mods')
