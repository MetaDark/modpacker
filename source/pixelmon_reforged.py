from base import Mod
from bs4 import BeautifulSoup
from typing import Iterable
from unshortenit.modules import AdfLy
from url import Url, urljoin
import requests

class PixelmonReforged(Mod):
    def url(self) -> Url:
        return Url('https://reforged.gg')

    def doc(self) -> Url:
        return Url('https://pixelmonmod.com/wiki')

    def latest(self, mc_version: str) -> Iterable[Url]:
        if mc_version != '1.12.2':
            raise LookupError('unsupported minecraft version: {}'.format(mc_version))

        url = self.url()
        res = requests.get(url)
        page = BeautifulSoup(res.text, 'lxml')
        download = urljoin(url, page.find('a', 'download').get('href'))
        return [self.resolve_download_url(download)]

    def resolve_download_url(self, url: Url) -> Url:
        unshortener = AdfLy()
        return Url(unshortener.unshorten(url))
