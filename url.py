from typing import NewType
from urllib.parse import urljoin, urlparse, quote as urlquote, unquote as urlunquote
import posixpath

Url = NewType('Url', str)

# Similar to urljoin, but constructs url from path segments instead of relative url
def urlpath(base: Url, *segments: str) -> Url:
    base = Url(base.rstrip('/'))
    url = '/'.join((urlquote(segment, safe='') for segment in segments))
    return Url('{}/{}'.format(base, url))

def filename(url: Url) -> str:
    return urlunquote(posixpath.basename(urlparse(url).path))
