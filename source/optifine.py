from base import Mod
from bs4 import BeautifulSoup, Tag
from typing import Iterable
from url import Url, urlpath, urljoin
import requests

class OptiFine(Mod):
    def __init__(self, session: requests.Session) -> None:
        self.session = session

    def url(self) -> Url:
        return Url('https://optifine.net')

    def doc(self) -> Url:
        return Url('https://github.com/sp614x/optifine/tree/master/OptiFineDoc/doc')

    def latest(self, mc_version: str) -> Iterable[Url]:
        url = urlpath(self.url(), 'downloads')
        res = self.session.get(url)
        page = BeautifulSoup(res.text, 'lxml')
        download = self.resolve_download_section(page, mc_version)
        return (self.resolve_download_url(url) for url in download)

    def resolve_download_section(self, page: Tag, mc_version: str) -> Iterable[Url]:
        version_header = page.find(class_='downloads').find('h2', string='Minecraft {}'.format(mc_version))
        if not version_header:
            raise LookupError('\'optifine\' doesn\'t have a release for minecraft {}'.format(mc_version))

        downloads = version_header.find_next_sibling(class_='downloadTable')
        return [downloads.find(class_='downloadLineMirror').find('a').get('href')]

    def resolve_download_url(self, url: Url) -> Url:
        res = self.session.get(url)
        return urljoin(url, BeautifulSoup(res.text, 'lxml').find(id='Download').find('a').get('href'))
