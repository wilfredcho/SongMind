import re

from newtunes.sites.Base import Base
from newtunes.sites.common.util import format_text, proc_info


class TopHitRu(Base):
    def proc_row(self, row, chart):
        cur_pos = format_text(row.find("div", {"class": "position"}).text)
        diff_pos = format_text(
            row.find("div", {"class": re.compile(r"position-histograma")}).text)
        if diff_pos == '=':
            last_pos = cur_pos
        else:
            if isinstance(diff_pos, str):
                last_pos = diff_pos
            else:
                last_pos = cur_pos + diff_pos
        title = format_text(row.find("a", {"class": "black"}).text)
        artist = format_text(row.find("a", {"class": "track_name black"}).text)
        return proc_info(chart, cur_pos, last_pos, title, artist)

    def run(self, soup, chart):
        table = soup.find("table", {"class": "table-list"})
        rows = table.find_all("tr", {"class": "b-chart-item "})
        return [self.proc_row(row, chart)
                for row in rows if bool(self.proc_row(row, chart))]
