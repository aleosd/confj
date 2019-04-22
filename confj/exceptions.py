class ConfigException(Exception):
    pass


class ConfigLoadException(ConfigException):
    pass


class NoConfigOptionError(ConfigException):
    pass
