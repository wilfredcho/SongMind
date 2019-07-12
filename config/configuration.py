import yaml


class Configuration(object):

    def __init__(self):
        with open("./config/config.yml", 'r') as ymlfile:
            self._cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)

    @property
    def cfg(self):
        return self._cfg
