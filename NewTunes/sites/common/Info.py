from ... import config as constants


class Info(object):

    def __init__(self, cur_pos, last_pos, title, artist):
        self.cur_pos = int(cur_pos)
        if isinstance(last_pos, str):
            if last_pos.lower() in constants.RE:
                self.last_pos = -1
            else:
                self.last_pos = 1000
        else:
            self.last_pos = last_pos
        self.title = str(title)
        self.artist = str(artist)
