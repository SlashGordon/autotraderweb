import configparser
import os
import sys


class Config:
    @staticmethod
    def get_config(configfile=None):
        """
        Returns the config file.
        :return:
        """
        config = configparser.ConfigParser()

        if configfile is None:
            config_file_name = 'config_test.ini' if sys.gettrace() else 'config.ini'
            configfile = os.path.join(os.path.abspath(os.path.join(__file__, os.pardir)),
                                      '..', config_file_name)
        if not os.path.exists(configfile):
            raise FileNotFoundError("Config file not found.")

        config.read(configfile)
        return config
