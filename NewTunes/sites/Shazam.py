from NewTunes.sites.Base import Base
from NewTunes.sites.common.util import format_text, proc_info


class Shazam(Base):
    def proc_row(self, row, chart):
        cur_pos = format_text(row.find("span", {"class": "number"}).text)
        last_pos = chart.condit['enter'] + 1
        title = format_text(row.find("div", {"class": "title"}).text)
        artist = format_text(row.find("div", {"class": "artist"}).text)
        return proc_info(chart, cur_pos, last_pos, title, artist)

    def run(self, soup, chart):
        rows = soup.find_all("li", {"itemprop": "track"})
        return [self.proc_row(row, chart)
                for row in rows if bool(self.proc_row(row, chart))]
