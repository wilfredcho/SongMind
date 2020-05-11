from newtunes.sites.Base import Base
from newtunes.sites.common.util import format_text, proc_info
import string

class Shazam(Base):
    def proc_row(self, row, chart):
        cur_pos = ''.join(char for char in format_text(row.find("div", {"class": "flex-reset number"}).text) if char not in set(string.punctuation))
        last_pos = chart.max + 1
        title = format_text(row.find("div", {"class": "title"}).text)
        artist = format_text(row.find("div", {"class": "artist"}).text)
        return proc_info(chart, cur_pos, last_pos, title, artist)

    def run(self, soup, chart):
        rows = soup.find_all("li", {"itemprop": "track"})
        return [self.proc_row(row, chart)
                for row in rows if bool(self.proc_row(row, chart))]
