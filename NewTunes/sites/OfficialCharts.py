from newtunes.sites.Base import Base
from newtunes.sites.common.util import format_text, proc_info


class OfficialCharts(Base):

    def proc_row(self, row, chart):
        if row.find("span", {"class": "position"}):
            cur_pos = format_text(row.find("span", {"class": "position"}).text)
            last_pos = format_text(
                row.find("span", {"class": "last-week"}).text)
            sub_post = row.find("div", {"class": "title-artist"})
            title = format_text(sub_post.find("div", {"class": "title"}).text)
            artist = format_text(sub_post.find(
                "div", {"class": "artist"}).text)
            return proc_info(chart, cur_pos, last_pos, title, artist)

    def run(self, soup, chart):
        table = soup.find("table", {"class": "chart-positions"})
        rows = table.find_all('tr')
        return [self.proc_row(row, chart)
                for row in rows if bool(self.proc_row(row, chart))]
