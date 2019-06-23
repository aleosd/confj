import json

from confj.exceptions import NoConfigOptionError, ConfigException


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
        return "<class 'ConfigData'>: {}".format(json.dumps(
            self._data, cls=ConfigEncoder))

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
