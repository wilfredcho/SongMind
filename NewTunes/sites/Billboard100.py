from NewTunes.sites.Base import Base
from NewTunes.sites.common.util import format_text, proc_info


class Billboard100(Base):
    def proc_row(self, row, chart):
        title = format_text(
            row.find("span", {"class": "chart-element__information__song text--truncate color--primary"}).text)
        artist = format_text(
            row.find("span", {"class": "chart-element__information__artist text--truncate color--secondary"}).text)
        cur_pos = format_text(
            row.find("span", {"class": "chart-element__rank__number"}).text)
        last_pos = format_text(row.find(
            "span", {"class": "chart-element__information__delta__text text--default"}).text)
        return proc_info(chart, cur_pos, last_pos, title, artist)

    def run(self, soup, chart):
        rows = soup.find_all("li", {"class": "chart-list__element display--flex"})
        return [self.proc_row(row, chart)
                          for row in rows if bool(self.proc_row(row, chart))]
