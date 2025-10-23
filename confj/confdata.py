from __future__ import annotations

import json
import pprint
import typing as t

from confj.exceptions import ConfigException, NoConfigOptionError


class ConfigEncoder(json.JSONEncoder):
    # pylint: disable=E0202
    def default(self, o: t.Any) -> t.Any:
        if isinstance(o, ConfigData):
            # pylint: disable=W0212
            return o._data
        return o

    def encode(self, o: t.Any) -> str:
        if isinstance(o, ConfigData):
            # pylint: disable=W0212
            return json.dumps(o._data, cls=ConfigEncoder)
        return super(ConfigEncoder, self).encode(o)


class ConfigData:
    def __init__(
        self, data: ConfigData | dict[str, t.Any] | None = None
    ) -> None:
        self._data = data or dict()
        super(ConfigData, self).__init__()

    def __getattr__(self, item: str) -> t.Any:
        if item in self._data:
            if isinstance(self._data[item], ConfigData):
                return self._data[item]

            if isinstance(self._data[item], dict):
                return ConfigData(self._data[item])

            return self._data[item]
        raise NoConfigOptionError("No such config option: {}".format(item))

    def __getitem__(self, key: str) -> t.Any:
        try:
            return self._data[key]
        except KeyError:
            raise NoConfigOptionError("No such config option: {}".format(key))

    def __setitem__(self, key: str, value: t.Any) -> None:
        self._data[key] = value

    def __contains__(self, item: str) -> bool:
        return item in self._data

    def __eq__(self, other: t.Any) -> bool:
        return self._data == other

    def __repr__(self) -> str:
        return "<class 'ConfigData'>: {}".format(
            json.dumps(self._data, cls=ConfigEncoder)
        )

    def __str__(self) -> str:
        return json.dumps(self._data, cls=ConfigEncoder)

    def __iter__(self) -> t.Iterator[str]:
        return iter(self.keys())

    def __len__(self) -> int:
        return len(self._data)

    def __hash__(self) -> int:
        return hash(str(self._data))

    def __bool__(self) -> bool:
        return bool(self._data)

    def keys(self) -> list[str]:
        return sorted(list(self._data.keys()))

    def get(self, key: str, default: t.Any = None) -> t.Any:
        try:
            return self.__getitem__(key)
        except NoConfigOptionError:
            return default

    def items(self) -> list[t.Any]:
        return list(self._data.items())

    def c_format(self) -> str:
        return pprint.pformat(self._data, indent=2)

    def c_pprint(self) -> None:
        return pprint.pprint(self._data, indent=2)

    def set(self, key: str, value: t.Any) -> None:
        if not self._data:
            self._data = {}
        if not isinstance(self._data, dict):
            raise ConfigException(
                'Expected data to be of dict type to proceed with "set" '
                f"operation, got {type(value)} instead"
            )
        self._data[key] = value
