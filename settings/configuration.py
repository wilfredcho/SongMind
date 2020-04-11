import yaml

from common.singleton import Singleton


class Configuration(metaclass=Singleton):

    def __init__(self):
        with open("settings/config.yml", 'r') as ymlfile:
            self._cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)

    @property
    def cfg(self):
        return self._cfg
