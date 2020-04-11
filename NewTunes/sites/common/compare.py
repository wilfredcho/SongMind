from newtunes import config as constants


def reenter(info, val):
    return info.cur_pos.lower() in constants.RE

def enter(info, val):
    return info.last_pos > val and info.cur_pos <= val
