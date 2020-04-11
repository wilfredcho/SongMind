from newtunes.sites.Base import Base
from newtunes.sites.common.util import format_text, proc_info


class AriaCharts(Base):
    def proc_row(self, row, chart):
        if row.find("td", {"class": "ranking"}):
            cur_pos = format_text(row.find("td", {"class": "ranking"}).text)
            try:
                int(cur_pos)
            except ValueError:
                cur_pos = ''.join(char for char in cur_pos if char.isdigit())
            last_pos = format_text(
                row.find("td", {"class": "chart-grid-column"}).text)
            if last_pos:
                sub_post = row.find("td", {"class": "title-artist"})
                title = format_text(sub_post.find(
                    "div", {"class": "item-title"}).text)
                artist = format_text(sub_post.find(
                    "div", {"class": "artist-name"}).text)
                return proc_info(chart, cur_pos, last_pos, title, artist)

    def run(self, soup, chart):
        table = soup.find("table", {"id": "tbChartItems"})
        rows = table.find_all('tr')
        return [self.proc_row(row, chart)
                for row in rows if bool(self.proc_row(row, chart))]
