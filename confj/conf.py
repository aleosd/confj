import json
import os
import pathlib
from typing import Optional

from . import const
from .exceptions import ConfigLoadException, NoConfigOptionError, \
    ConfigException

try:
    from jsonschema import Draft7Validator, ValidationError
    from jsonschema.validators import extend
except ImportError:
    raise ImportError(
        'Cannot find "jsonschema" package. Either install it manually '
        'with pip, or install confj with validation option: '
        'pip install confj[validation]')


class ConfigEncoder(json.JSONEncoder):
    # pylint: disable=E0202
    def default(self, o):
        if isinstance(o, ConfigData):
            # pylint: disable=W0212
            return o._data
        return o

    def encode(self, o):
        if isinstance(o, ConfigData):
            # pylint: disable=W0212
            return json.dumps(o._data, cls=ConfigEncoder)
        return super(ConfigEncoder, self).encode(o)


# pylint: disable=W0613
def is_config(checker, instance):
    return (Draft7Validator.TYPE_CHECKER.is_type(instance, "object") or
            isinstance(instance, ConfigData))


TYPE_CHECKER = Draft7Validator.TYPE_CHECKER.redefine("object", is_config)

ConfigValidator = extend(Draft7Validator, type_checker=TYPE_CHECKER)
CONFIG_VALIDATOR = ConfigValidator(schema={"type": "object"})


class ConfigData:
    def __init__(self, data=None):
        self._data = data or dict()
        super(ConfigData, self).__init__()

    def __getattr__(self, item: str):
        if item in self._data:
            if isinstance(self._data[item], ConfigData):
                return self._data[item]

            if isinstance(self._data[item], dict):
                return ConfigData(self._data[item])

            return self._data[item]
        raise NoConfigOptionError('No such config option: {}'.format(item))

    def __getitem__(self, key):
        try:
            return self._data[key]
        except KeyError:
            raise NoConfigOptionError('No such config option: {}'.format(key))

    def __contains__(self, item):
        return item in self._data

    def __eq__(self, other):
        return self._data == other

    def __repr__(self):
        return "<class 'ConfigData'>: {}".format(json.dumps(self._data, cls=ConfigEncoder))

    def __str__(self):
        return json.dumps(self._data, cls=ConfigEncoder)

    def __iter__(self):
        return iter(self._data.keys())

    def __len__(self):
        return len(self._data)

    def keys(self):
        return sorted(list(self._data.keys()))

    def get(self, key, default=None):
        try:
            return self.__getitem__(key)
        except NoConfigOptionError:
            return default

    def items(self):
        if isinstance(self._data, (dict, ConfigData)):
            return self._data.items()
        raise ConfigException('Called "items" on non-dict config option')

    def c_format(self):
        import pprint
        return pprint.pformat(self._data, indent=2)

    def c_pprint(self):
        import pprint
        return pprint.pprint(self._data, indent=2)

    def c_validate(self, schema, do_raise=False):
        try:
            CONFIG_VALIDATOR.validate(self, schema)
            return True
        except ValidationError:
            if do_raise:
                raise
            return False


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
                self._data[config_name] = ''
            else:
                config_data = json.loads(file.read_text())
                self.add_subconfig(config_name, config_data)

    def add_subconfig(self, name, config_data):
        if name in self._data:
            raise ConfigException('Config already contains "{}" option!'.format(
                name))
        self._data[name] = ConfigData(config_data)

    def __repr__(self):
        return "<class 'Config'>: {}".format(self)
