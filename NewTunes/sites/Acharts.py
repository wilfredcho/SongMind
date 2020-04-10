from NewTunes.sites.Base import Base
from NewTunes.sites.common.util import format_text, proc_info


class Acharts(Base):
    def proc_row(self, row, chart):
        cur_pos = format_text(row.find("span", {"itemprop": "position"}).text)
        last_pos = row.find("span", {"class": "Sub subStatsPrev"}).text
        last_pos = format_text(
            ''.join(char for char in last_pos if char.isalnum()))
        title_artist = row.find_all("span", {"itemprop": "name"})
        title = title_artist[0].text
        artist = ''.join(artist.text for artist in title_artist[1:])
        return proc_info(chart, cur_pos, last_pos, title, artist)

    def run(self, soup, chart):
        table = soup.find("table", {"id": "ChartTable"})
        rows = table.find_all("tr", {"itemprop": "itemListElement"})
        return [self.proc_row(row, chart)
                for row in rows if bool(self.proc_row(row, chart))]
