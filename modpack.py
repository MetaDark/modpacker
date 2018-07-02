#!/usr/bin/env python3

from abc import ABC, abstractmethod
from bs4 import BeautifulSoup
from itertools import takewhile
from urllib.parse import quote as urlquote, urljoin
import re
import requests

class Repo(ABC):
    @abstractmethod
    def url(self):
        pass

    @abstractmethod
    def mod(self, mod):
        pass

class Mod(ABC):
    @abstractmethod
    def url(self):
        pass

    def doc(self):
        return self.url()

    @abstractmethod
    def latest(self, mc_version):
        pass

class CurseForge(Repo):
    def __init__(self):
        self.mc_versions = None

    def url(self):
        return 'https://minecraft.curseforge.com'

    def mod(self, mod):
        return CurseForgeMod(self, mod)

    def resolve_mc_version(self, mc_version):
        if not self.mc_versions:
            res = requests.get('{}/{}'.format(self.url(), 'mc-mods'))
            page = BeautifulSoup(res.text, 'lxml')
            self.mc_versions = dict((option.string.strip(), option.get('value'))
                                    for option in page.find('select', id='filter-game-version').find_all('option'))

        try:
            return self.mc_versions[mc_version]
        except:
            raise LookupError('failed to find minecraft version: {}'.format(mc_version))

class CurseForgeMod(Mod):
    def __init__(self, curse_forge, mod):
        self.curse_forge = curse_forge
        self.mod = mod

    def url(self):
        return '{}/projects/{}'.format(self.curse_forge.url(), urlquote(self.mod, safe=''))

    def doc(self):
        url = self.url()
        res = requests.get(url)
        page = BeautifulSoup(res.text, 'lxml')
        return next((urljoin(url, link.get('href'))
                     for link in page.find(class_='e-menu').find_all('a')
                     if link.string.strip() == 'Wiki'), url)

    def latest(self, mc_version):
        url = '{}/{}'.format(self.url(), 'files')
        res = requests.get(url, params = {
            'filter-game-version': self.curse_forge.resolve_mc_version(mc_version),
            'sort': 'releasetype',
        })

        if not res:
            raise LookupError('failed to find mod: {}'.format(self.mod))

        page = BeautifulSoup(res.text, 'lxml')
        for row in page.find('table', class_='listing-project-file').find_all('tr'):
            if row.find(class_='release-phase'):
                # TODO: Grab dependencies
                return [urljoin(url, row.find(class_='project-file-download-button').find('a').get('href'))]

        raise LookupError('\'{}\' doesn\'t have a release for minecraft {}'.format(self.mod, mc_version))        

class Micdoodle8(Repo):
    def url(self):
        return 'https://micdoodle8.com'

    def mod(self, mod):
        mods = {
            'galacticraft': Galacticraft,
        }

        try:
            return mods[mod](self)
        except KeyError:
            raise LookupError('unsupported mod: {}'.format(mod))

class Galacticraft(Mod):
    def __init__(self, micdoodle8):
        self.micdoodle8 = micdoodle8

    def url(self):
        return '{}/mods/galacticraft'.format(self.micdoodle8.url())

    def doc(self):
        return 'https://wiki.micdoodle8.com/wiki/Galacticraft'

    def latest(self, mc_version):
        url = '{}/{}'.format(self.url(), 'downloads')
        res = requests.get(url)
        page = BeautifulSoup(res.text, 'lxml')
        downloads = page.find(id=self.resolve_mc_version(page, mc_version))
        latest = self.resolve_download_section(downloads, 'Promoted')
        return [self.resolve_download_url(url) for url in latest]

    def resolve_mc_version(self, url, mc_version):
        versions = url.find('select', id='mc_version')
        try:
            return next(option.get('value')
                        for option in versions.find_all('option', string=mc_version))
        except StopIteration:
            raise LookupError('\'galacticraft\' doesn\'t have a release for minecraft {}'.format(mc_version))

    def resolve_download_section(self, downloads, section):
        # TODO: Support scraping links from 'Latest' sections
        links = downloads.find('h4', string=section).find_next_siblings('a')
        links = takewhile(lambda elem: elem.name != 'h4', links)
        return [link.get('href') for link in links]

    def resolve_download_url(self, url):
        res = requests.get(url)
        return re.search(r'var phpStr = "(.*?)"', res.text)[1]

class OptiFine(Mod):
    def url(self):
        return 'https://optifine.net'

    def doc(self):
        return 'https://github.com/sp614x/optifine/tree/master/OptiFineDoc/doc'

    def latest(self, mc_version):
        url = '{}/{}'.format(self.url(), 'downloads')
        res = requests.get(url)
        page = BeautifulSoup(res.text, 'lxml')
        download = self.resolve_download_section(page, mc_version)
        return [self.resolve_download_url(url) for url in download]

    def resolve_download_section(self, url, mc_version):
        version_header = url.find(class_='downloads').find('h2', string='Minecraft {}'.format(mc_version))
        if not version_header:
            raise LookupError('\'optifine\' doesn\'t have a release for minecraft {}'.format(mc_version))

        downloads = version_header.find_next_sibling(class_='downloadTable')
        return [downloads.find(class_='downloadLineMirror').find('a').get('href')]

    def resolve_download_url(self, url):
        res = requests.get(url)
        return urljoin(url, BeautifulSoup(res.text, 'lxml').find(id='Download').find('a').get('href'))

class PixelmonReforged(Mod):
    def url(self):
        return 'https://reforged.gg'

    def doc(self):
        return 'https://pixelmonmod.com/wiki'

    def latest(self, mc_version):
        if mc_version != '1.12.2':
            raise LookupError('unsupported minecraft version: {}'.format(mc_version))

        url = self.url()
        res = requests.get(url)
        page = BeautifulSoup(res.text, 'lxml')

        # TODO: Bypass adfly
        return [urljoin(url, page.find('a', 'download').get('href'))]

# Examples:
curse_forge = CurseForge()
print(curse_forge.url())

invtweaks = curse_forge.mod('inventory-tweaks')
print(invtweaks.url())
print(invtweaks.doc())
print(invtweaks.latest('1.12.2'))

jei = curse_forge.mod('jei')
print(jei.url())
print(jei.doc())
print(jei.latest('1.12.2'))

micdoodle8 = Micdoodle8()
print(micdoodle8.url())
galacticraft = micdoodle8.mod('galacticraft')
print(galacticraft.url())
print(galacticraft.doc())
print(galacticraft.latest('1.12.2'))

optifine = OptiFine()
print(optifine.url())
print(optifine.doc())
print(optifine.latest('1.12.2'))

pixelmon = PixelmonReforged()
print(pixelmon.url())
print(pixelmon.doc())
print(pixelmon.latest('1.12.2'))
