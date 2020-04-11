from newtunes.sites.Base import Base
from newtunes.sites.common.util import format_text, proc_info


class HitListen(Base):
    def proc_row(self, row, chart):
        if row.find("div", {"id": "denneuge"}):
            cur_pos = format_text(row.find("div", {"id": "denneuge"}).text)
            last_pos = format_text(row.find("div", {"id": "sidsteuge"}).text)
            sub_post = row.findNext("div", {"id": "udgivelse"})
            title = format_text(sub_post.find("div", {"id": "titel"}).text)
            artist = format_text(sub_post.find(
                "div", {"id": "artistnavn"}).text)
            return proc_info(chart, cur_pos, last_pos, title, artist)
        if row.find("div", {"id": "denneugeny"}):
            cur_pos = format_text(row.find("div", {"id": "denneugeny"}).text)
            last_pos = format_text(row.find("div", {"id": "sidsteuge"}).text)
            sub_post = row.findNext("div", {"id": "udgivelse"})
            title = format_text(sub_post.find("div", {"id": "titel"}).text)
            artist = format_text(sub_post.find(
                "div", {"id": "artistnavn"}).text)
            return proc_info(chart, cur_pos, last_pos, title, artist)

    def run(self, soup, chart):
        rows = soup.find_all("div", {"id": "linien"})
        return [self.proc_row(row, chart)
                for row in rows if bool(self.proc_row(row, chart))]
