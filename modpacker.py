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

sources = {
    'micdoodle8.com': Micdoodle8(),
    'minecraft.curseforge.com': CurseForge(),
    'optifine.net': OptiFine(),
    'reforged.gg': PixelmonReforged(),
}

if __name__ == '__main__':
    args = docopt(__doc__, version='modpacker 1.0')
    with open(args['<modpack>'], 'r') as modpack:
        app, version = next(modpack).split()
        for mod in modpack:
            source_id, *mod_id = mod.split()
            source = sources[source_id]
            if isinstance(source, Mod):
                print(source.latest(version))
            elif isinstance(source, Repo):
                print(source.mod(mod_id[0]).latest(version))
