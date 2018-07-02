#!/usr/bin/env python3

from abc import ABC, abstractmethod
from bs4 import BeautifulSoup
from itertools import takewhile
from urllib.parse import quote as urlquote, urljoin
import re
import requests

class Source(ABC):
    @abstractmethod
    def homepage(self):
        pass

    @abstractmethod
    def modpage(self, mod):
        pass

    @abstractmethod
    def latest(self, mod, mc_version):
        pass

class CurseForge(Source):
    def __init__(self):
        self.mc_versions = None

    def homepage(self):
        return 'https://minecraft.curseforge.com'

    def modpage(self, mod):
        return '{}/projects/{}'.format(self.homepage(), urlquote(mod, safe=''))

    def latest(self, mod, mc_version):
        url = '{}/{}'.format(self.modpage(mod), 'files')
        res = requests.get(url, params = {
            'filter-game-version': self.resolve_mc_version(mc_version),
            'sort': 'releasetype',
        })

        if not res:
            raise LookupError('failed to find mod: {}'.format(mod))

        page = BeautifulSoup(res.text, 'lxml')
        for row in page.find('table', class_='listing-project-file').find_all('tr'):
            if row.find(class_='release-phase'):
                # TODO: Grab dependencies
                return [urljoin(url, row.find(class_='project-file-download-button').find('a').get('href'))]

        raise LookupError('\'{}\' doesn\'t have a release for minecraft {}'.format(mod, mc_version))

    def resolve_mc_version(self, mc_version):
        if not self.mc_versions:
            res = requests.get('{}/{}'.format(self.homepage(), 'mc-mods'))
            page = BeautifulSoup(res.text, 'lxml')
            self.mc_versions = dict((option.text.strip(), option.get('value'))
                                    for option in page.find('select', id='filter-game-version').find_all('option'))

        try:
            return self.mc_versions[mc_version]
        except:
            raise LookupError('failed to find minecraft version: {}'.format(mc_version))

class Micdoodle8(Source):
    def homepage(self):
        return 'https://micdoodle8.com'

    def modpage(self, mod):
        return '{}/mods/{}'.format(self.homepage(), urlquote(mod, safe=''))

    def latest(self, mod, mc_version):
        mods = {
            'galacticraft': self.latest_galacticraft,
        }

        try:
            return mods[mod](mc_version)
        except KeyError:
            raise LookupError('unsupported mod: {}'.format(mod))

    def latest_galacticraft(self, mc_version):
        url = '{}/{}'.format(self.modpage('galacticraft'), 'downloads')
        res = requests.get(url)

        if not res:
            raise LookupError('failed to find mod: {}'.format('galacticraft'))

        page = BeautifulSoup(res.text, 'lxml')
        downloads = page.find(id=self.resolve_mc_version(page, 'galacticraft', mc_version))
        latest = self.resolve_download_section(downloads, 'Promoted')
        return [self.resolve_download_url(url) for url in latest]

    def resolve_mc_version(self, modpage, mod, mc_version):
        versions = modpage.find('select', id='mc_version')
        try:
            return next(option.get('value')
                        for option in versions.find_all('option', string=mc_version))
        except StopIteration:
            raise LookupError('\'{}\' doesn\'t have a release for minecraft {}'.format(mod, mc_version))

    def resolve_download_section(self, downloads, section):
        # TODO: Support scraping links from 'Latest' sections
        links = downloads.find('h4', string=section).find_next_siblings('a')
        links = takewhile(lambda elem: elem.name != 'h4', links)
        return (link.get('href') for link in links)

    def resolve_download_url(self, url):
        res = requests.get(url)
        return re.search(r'var phpStr = "(.*?)"', res.text)[1]

class OptiFine(Source):
    def homepage(self):
        return 'https://optifine.net'

    def modpage(self, mod):
        return self.homepage()

    def latest(self, mod, mc_version):
        if mod:
            raise LookupError('source provides only one mod')

        url = '{}/{}'.format(self.modpage(mod), 'downloads')
        res = requests.get(url)

        page = BeautifulSoup(res.text, 'lxml')
        version_header = page.find(class_='downloads').find('h2', string='Minecraft {}'.format(mc_version))
        if not version_header:
            raise LookupError('failed to find minecraft version: {}'.format(mc_version))

        downloads = version_header.find_next_sibling(class_='downloadTable')
        download_url = downloads.find(class_='downloadLineMirror').find('a').get('href')
        return self.resolve_download_url(download_url)

    def resolve_download_url(self, url):
        res = requests.get(url)
        print(res.text)

# Examples:
source = CurseForge()
print(source.homepage())
print(source.modpage('inventory-tweaks'))
print(source.latest('inventory-tweaks', '1.12.2'))

source = Micdoodle8()
print(source.homepage())
print(source.modpage('galacticraft'))
print(source.latest('galacticraft', '1.12.2'))

# source = OptiFine()
# print(source.homepage())
# print(source.modpage(None))
# source.latest(None, '1.12.2')
