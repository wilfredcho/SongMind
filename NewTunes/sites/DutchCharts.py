from newtunes.sites.Base import Base
from newtunes.sites.common.util import format_text, proc_info


class DutchCharts(Base):
    def proc_row(self, row, chart):
        cur_pos = format_text(row.find_all("td", {"class": "text"})[0].text)
        last_pos = format_text(row.find_all("td")[1].text)
        if last_pos is None:
            last_pos = 101
        artist_title = row.find("a", {"class": "navb"}).text
        artist = row.find("a", {"class": "navb"}).select("b")[0].text
        title = artist_title.replace(artist, "")
        return proc_info(chart, cur_pos, last_pos, title, artist)

    def run(self, soup, chart):
        table = soup.find("table")
        rows = table.find_all("tr", {"class": "charts"})
        return [self.proc_row(row, chart)
                for row in rows if bool(self.proc_row(row, chart))]
