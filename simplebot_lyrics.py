from urllib.parse import quote, unquote_plus

import bs4
import requests
import simplebot
from simplebot.bot import Replies

__version__ = "1.0.0"
HEADERS = {
    "user-agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:60.0)"
    " Gecko/20100101 Firefox/60.0"
}


@simplebot.command
def lyrics(payload: str, replies: Replies) -> None:
    """Get song lyrics."""
    base_url = "https://www.lyrics.com"
    url = "{}/lyrics/{}".format(base_url, quote(payload))
    with requests.get(url, headers=HEADERS) as r:
        r.raise_for_status()
        soup = bs4.BeautifulSoup(r.text, "html.parser")
    best_matches = soup.find("div", class_="best-matches")
    a = best_matches and best_matches.a
    if not a:
        soup = soup.find("div", class_="sec-lyric")
        a = soup and soup.a
    if a:
        artist, name = map(unquote_plus, a["href"].split("/")[-2:])
        url = base_url + a["href"]
        with requests.get(url, headers=HEADERS) as r:
            r.raise_for_status()
            soup = bs4.BeautifulSoup(r.text, "html.parser")
            lyric = soup.find(id="lyric-body-text")
            if lyric:
                text = "🎵 {} - {}\n\n{}".format(name, artist, lyric.get_text())
                replies.add(text=text)
                return

    replies.add(text="No results for: {}".format(payload))


class TestPlugin:
    def test_lyrics(self, mocker):
        msg = mocker.get_one_reply("/lyrics Baby Jane")
        assert "🎵" in msg.text
