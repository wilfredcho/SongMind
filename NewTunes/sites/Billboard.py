from NewTunes.sites.Base import Base
from NewTunes.sites.common.util import format_text, proc_info


class Billboard(Base):
    def proc_trow(self, row, chart):
        cur_pos = 1
        try:
            last_pos = format_text(
                row.find("div", {"class": "chart-number-one__last-week"}).text)
        except AttributeError:
            last_pos = 1
        title = format_text(
            row.find("div", {"class": "chart-number-one__title"}).text)
        try:
            artist = format_text(
                row.find("div", {"class": "chart-number-one__artist"}).find("a").text)
        except AttributeError:
            artist = format_text(
                row.find("div", {"class": "chart-number-one__artist"}).text)
        return proc_info(chart, cur_pos, last_pos, title, artist)

    def proc_row(self, row, chart):
        title = format_text(
            row.find("span", {"class": "chart-list-item__title-text"}).text)
        try:
            artist = format_text(
                row.find("div", {"class": "chart-list-item__artist"}).find("a").text)
        except AttributeError:
            artist = format_text(
                row.find("div", {"class": "chart-list-item__artist"}).text)
        try:
            cur_pos = format_text(
                row.find("div", {"class": "chart-list-item__rank"}).text)
        except AttributeError:
            cur_pos = format_text(row.find(
                "div", {"class": "chart-list-item__rank chart-list-item__rank--long"}).text)
        stats = row.find("div", {"class": "chart-list-item__stats"})
        if stats:
            last_pos = format_text(stats.find(
                "div", {"class": "chart-list-item__last-week"}).text)
        else:
            last_pos = "new"
        return proc_info(chart, cur_pos, last_pos, title, artist)

    def run(self, soup, chart):
        top = soup.find(
            "div", {"class": "container container--no-background chart-number-one"})
        top_row = top.find("div", {"class": "chart-number-one__info"})
        if bool(self.proc_trow(top_row, chart)):
            top_row = [self.proc_trow(top_row, chart)]
        else:
            top_row = []
        rows = soup.find_all("div", {"class": "chart-list-item"})
        return top_row + [self.proc_row(row, chart)
                          for row in rows if bool(self.proc_row(row, chart))]
