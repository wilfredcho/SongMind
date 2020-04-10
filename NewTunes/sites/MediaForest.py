import itertools

from NewTunes.sites.Base import Base
from NewTunes.sites.common.util import format_text, proc_info


class MediaForest(Base):

    def proc_row(self, row, chart):
        cells = row.findAll('td')
        cur_pos = format_text(cells[0].text)
        last_pos = format_text(cells[1].text)
        sub_post = cells[3].contents
        title = format_text(sub_post[3])
        artist = format_text(sub_post[1].text)
        return proc_info(chart, cur_pos, last_pos, title, artist)

    def run(self, soup, chart):
        rows = soup.find_all("tbody", {"id": "tb_WeeklyChartRadioLocal"})[
            0].findAll('tr')
        return [self.proc_row(row, chart)
                for row in rows if bool(self.proc_row(row, chart))]
