from base import Mod
from bs4 import BeautifulSoup
from typing import List
from url import Url, urljoin
import requests

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
