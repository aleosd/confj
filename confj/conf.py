import json
import os
import pathlib
from typing import Optional

from confj.confdata import ConfigData
from . import const
from .exceptions import ConfigLoadException, ConfigException


class Config(ConfigData):
    def __init__(self, default_config_path=None, autoload=False):
        super(Config, self).__init__()
        self.default_config_path = default_config_path
        if autoload:
            self.load()

    def load(self, config_path=None):
        path = pathlib.Path(self._select_config_path(config_path))
        if not path.exists():
            raise ConfigLoadException('Path "{}" does not exist'.format(path))
        if path.is_dir():
            return self._load_from_dir(path)
        if path.is_file():
            return self._load_from_file(path)
        raise ConfigLoadException('Expected path {} to be file or '
                                  'directory'.format(path))

    def load_from_obj(self, python_object):
        self._data = ConfigData(data=python_object)

    def _select_config_path(self, config_path: Optional[str] = None) -> str:
        if config_path:
            return config_path
        if self.default_config_path:
            return self.default_config_path
        env_config_path = os.environ.get(const.ENV_CONF_PATH_NAME)
        if env_config_path:
            return env_config_path
        raise ConfigException('Please provide path to load config from')

    def _load_from_file(self, file_path):
        self._data = ConfigData(json.loads(file_path.read_text()))

    def _load_from_dir(self, dir_path: pathlib.Path):
        for file in dir_path.iterdir():
            if not file.is_file():
                continue
            config_name = file.stem
            file_contents = file.read_text()
            if not file_contents.strip():
                self._data[config_name] = ConfigData(data='')
            else:
                config_data = json.loads(file.read_text())
                self.add_subconfig(config_name, config_data)

    def c_validate(self, schema, do_raise=False):
        from jsonschema import ValidationError
        from .validation import CONFIG_VALIDATOR
        try:
            CONFIG_VALIDATOR.validate(self, schema)
            return True
        except ValidationError:
            if do_raise:
                raise
            return False

    def add_subconfig(self, name, config_data):
        if name in self._data:
            raise ConfigException('Config already contains "{}" option!'.format(
                name))
        self._data[name] = ConfigData(config_data)

    def __repr__(self):
        return "<class 'Config'>: {}".format(self)
