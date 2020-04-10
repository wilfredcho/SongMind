class ChartCss(object):
    def __init__(self, chart):
        for key in chart:
            setattr(self, key, chart[key])
