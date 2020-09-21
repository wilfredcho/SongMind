from newtunes.sites.Base import Base
from newtunes.sites.common.util import format_text, proc_info


class AriaCharts(Base):
    def proc_row(self, row, chart):
        cur_pos = row.find("div", {"class": "c-chart-item__rank"}).text
        try:
            cur_pos = int(cur_pos)
        except ValueError:
            cur_pos = ''.join(char for char in cur_pos if char.isdigit())
        last_pos = format_text(
                row.find("p", {"class": "c-chart-item__week"}).text.split(' ')[0])
        artist = format_text(row.find("a", {"class": "c-chart-item__artist"}).text)
        title = format_text(row.find("a", {"class": "c-chart-item__title"}).text)
        return proc_info(chart, cur_pos, last_pos, title, artist)

    def run(self, soup, chart):
        table = soup.find("ul", {"class": "c-chart-list js-charts"})
        rows = table.find_all('li')
        return [self.proc_row(row, chart)
                for row in rows if bool(self.proc_row(row, chart))]
