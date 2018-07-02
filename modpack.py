#!/usr/bin/env python3

from abc import ABC, abstractmethod
from bs4 import BeautifulSoup, Tag
from itertools import takewhile
from typing import NewType, Dict, List, Optional
from urllib.parse import quote as urlquote, urljoin
import re
import requests

Url = NewType('Url', str)

# Similar to urljoin, but constructs url from path segments instead of relative url
def urlpath(base: Url, *segments: str) -> Url:
    base = Url(base.rstrip('/'))
    url = '/'.join((urlquote(segment, safe='') for segment in segments))
    return Url('{}/{}'.format(base, url))

class Mod(ABC):
    @abstractmethod
    def url(self) -> Url:
        pass

    def doc(self) -> Url:
        return self.url()

    @abstractmethod
    def latest(self, mc_version: str) -> List[Url]:
        pass

class Repo(ABC):
    @abstractmethod
    def url(self) -> Url:
        pass

    @abstractmethod
    def mod(self, mod: str) -> Mod:
        pass

class CurseForge(Repo):
    mc_versions: Optional[Dict[str, str]] = None

    def url(self) -> Url:
        return Url('https://minecraft.curseforge.com')

    def mod(self, mod: str) -> Mod:
        return CurseForgeMod(self, mod)

    def resolve_mc_version(self, mc_version: str) -> str:
        if not self.mc_versions:
            res = requests.get(urlpath(self.url(), 'mc-mods'))
            page = BeautifulSoup(res.text, 'lxml')
            self.mc_versions = dict((option.string.strip(), option.get('value'))
                                    for option in page.find('select', id='filter-game-version').find_all('option'))

        try:
            return self.mc_versions[mc_version]
        except:
            raise LookupError('failed to find minecraft version: {}'.format(mc_version))

class CurseForgeMod(Mod):
    def __init__(self, curse_forge: CurseForge, mod: str) -> None:
        self.curse_forge = curse_forge
        self.mod = mod

    def url(self) -> Url:
        return urlpath(self.curse_forge.url(), 'projects', self.mod)

    def doc(self) -> Url:
        url = self.url()
        res = requests.get(url)
        page = BeautifulSoup(res.text, 'lxml')
        return next((Url(urljoin(url, link.get('href')))
                     for link in page.find(class_='e-menu').find_all('a')
                     if link.string.strip() == 'Wiki'), url)

    def latest(self, mc_version: str) -> List[Url]:
        url = urlpath(self.url(), 'files')
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
                return [Url(urljoin(url, row.find(class_='project-file-download-button').find('a').get('href')))]

        raise LookupError('\'{}\' doesn\'t have a release for minecraft {}'.format(self.mod, mc_version))

class Micdoodle8(Repo):
    def url(self) -> Url:
        return Url('https://micdoodle8.com')

    def mod(self, mod: str) -> Mod:
        mods = {
            'galacticraft': Galacticraft,
        }

        try:
            return mods[mod](self)
        except KeyError:
            raise LookupError('unsupported mod: {}'.format(mod))

class Galacticraft(Mod):
    def __init__(self, micdoodle8: Micdoodle8) -> None:
        self.micdoodle8 = micdoodle8

    def url(self) -> Url:
        return urlpath(self.micdoodle8.url(), 'mods', 'galacticraft')

    def doc(self) -> Url:
        return Url('https://wiki.micdoodle8.com/wiki/Galacticraft')

    def latest(self, mc_version: str) -> List[Url]:
        url = urlpath(self.url(), 'downloads')
        res = requests.get(url)
        page = BeautifulSoup(res.text, 'lxml')
        downloads = page.find(id=self.resolve_mc_version(page, mc_version))
        latest = self.resolve_download_section(downloads, 'Promoted')
        return [self.resolve_download_url(url) for url in latest]

    def resolve_mc_version(self, page: Tag, mc_version: str) -> str:
        versions = page.find('select', id='mc_version')
        try:
            return next(option.get('value')
                        for option in versions.find_all('option', string=mc_version))
        except StopIteration:
            raise LookupError('\'{}\' doesn\'t have a release for minecraft {}'.format('galacticraft', mc_version))

    def resolve_download_section(self, downloads: Tag, section: str) -> List[Url]:
        # TODO: Support scraping links from 'Latest' sections
        links = downloads.find('h4', string=section).find_next_siblings('a')
        links = takewhile(lambda elem: elem.name != 'h4', links)
        return [Url(link.get('href')) for link in links]

    def resolve_download_url(self, url: Url) -> Url:
        res = requests.get(url)
        return Url(re.search(r'var phpStr = "(.*?)"', res.text)[1])

class OptiFine(Mod):
    def url(self) -> Url:
        return Url('https://optifine.net')

    def doc(self) -> Url:
        return Url('https://github.com/sp614x/optifine/tree/master/OptiFineDoc/doc')

    def latest(self, mc_version: str) -> List[Url]:
        url = urlpath(self.url(), 'downloads')
        res = requests.get(url)
        page = BeautifulSoup(res.text, 'lxml')
        download = self.resolve_download_section(page, mc_version)
        return [self.resolve_download_url(url) for url in download]

    def resolve_download_section(self, page: Tag, mc_version: str) -> List[Url]:
        version_header = page.find(class_='downloads').find('h2', string='Minecraft {}'.format(mc_version))
        if not version_header:
            raise LookupError('\'optifine\' doesn\'t have a release for minecraft {}'.format(mc_version))

        downloads = version_header.find_next_sibling(class_='downloadTable')
        return [Url(downloads.find(class_='downloadLineMirror').find('a').get('href'))]

    def resolve_download_url(self, url: Url) -> Url:
        res = requests.get(url)
        return Url(urljoin(url, BeautifulSoup(res.text, 'lxml').find(id='Download').find('a').get('href')))

class PixelmonReforged(Mod):
    def url(self) -> Url:
        return Url('https://reforged.gg')

    def doc(self) -> Url:
        return Url('https://pixelmonmod.com/wiki')

    def latest(self, mc_version: str) -> List[Url]:
        if mc_version != '1.12.2':
            raise LookupError('unsupported minecraft version: {}'.format(mc_version))

        url = self.url()
        res = requests.get(url)
        page = BeautifulSoup(res.text, 'lxml')

        # TODO: Bypass adfly
        return [Url(urljoin(url, page.find('a', 'download').get('href')))]

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
