from base import Repo, Mod
from bs4 import BeautifulSoup, Tag
from itertools import takewhile
from typing import Iterable
from url import Url, urlpath
import re
import requests

class Micdoodle8(Repo):
    def url(self) -> Url:
        return Url('https://micdoodle8.com')

    def mod(self, mod_id: str) -> Mod:
        try:
            return mods[mod_id](self)
        except KeyError:
            raise LookupError('unsupported mod: {}'.format(mod_id))

class Galacticraft(Mod):
    def __init__(self, micdoodle8: Micdoodle8) -> None:
        self.micdoodle8 = micdoodle8

    def url(self) -> Url:
        return urlpath(self.micdoodle8.url(), 'mods', 'galacticraft')

    def doc(self) -> Url:
        return Url('https://wiki.micdoodle8.com/wiki/Galacticraft')

    def latest(self, mc_version: str) -> Iterable[Url]:
        url = urlpath(self.url(), 'downloads')
        res = requests.get(url)
        page = BeautifulSoup(res.text, 'lxml')
        downloads = page.find(id=self.resolve_mc_version(page, mc_version))
        latest = self.resolve_download_section(downloads, 'Promoted')
        return (self.resolve_download_url(url) for url in latest)

    def resolve_mc_version(self, page: Tag, mc_version: str) -> str:
        versions = page.find('select', id='mc_version')
        try:
            return next(option.get('value')
                        for option in versions.find_all('option', string=mc_version))
        except StopIteration:
            raise LookupError('\'{}\' doesn\'t have a release for minecraft {}'.format('galacticraft', mc_version))

    def resolve_download_section(self, downloads: Tag, section: str) -> Iterable[Url]:
        # TODO: Support scraping links from 'Latest' sections
        links = downloads.find('h4', string=section).find_next_siblings('a')
        links = takewhile(lambda elem: elem.name != 'h4', links)
        return (link.get('href') for link in links)

    def resolve_download_url(self, url: Url) -> Url:
        res = requests.get(url)
        match = re.search(r'var phpStr = "(.*?)"', res.text)
        if not match:
            raise Exception('failed to resolve download url')

        return Url(match[1])

mods = {
    'galacticraft': Galacticraft,
}
