from base import Repo, Mod
from bs4 import BeautifulSoup
from typing import Iterable, Dict, Optional
from url import Url, urlpath, urljoin
import requests

class CurseForge(Repo):
    mc_versions: Optional[Dict[str, str]] = None

    def url(self) -> Url:
        return Url('https://minecraft.curseforge.com')

    def mod(self, mod_id: str) -> Mod:
        return CurseForgeMod(self, mod_id)

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
    def __init__(self, curseforge: CurseForge, mod_id: str) -> None:
        self.curseforge = curseforge
        self.mod_id = mod_id

    def url(self) -> Url:
        return urlpath(self.curseforge.url(), 'projects', self.mod_id)

    def doc(self) -> Url:
        url = self.url()
        res = requests.get(url)
        page = BeautifulSoup(res.text, 'lxml')
        return next((Url(urljoin(url, link.get('href')))
                     for link in page.find(class_='e-menu').find_all('a')
                     if link.string.strip() == 'Wiki'), url)

    def latest(self, mc_version: str) -> Iterable[Url]:
        url = urlpath(self.url(), 'files')
        res = requests.get(url, params = {
            'filter-game-version': self.curseforge.resolve_mc_version(mc_version),
            'sort': 'releasetype',
        })

        if not res:
            raise LookupError('failed to find mod: {}'.format(self.mod_id))

        page = BeautifulSoup(res.text, 'lxml')
        for row in page.find('table', class_='listing-project-file').find_all('tr'):
            if row.find(class_='release-phase'):
                # TODO: Grab dependencies
                return [Url(urljoin(url, row.find(class_='project-file-download-button').find('a').get('href')))]

        raise LookupError('\'{}\' doesn\'t have a release for minecraft {}'.format(self.mod_id, mc_version))
