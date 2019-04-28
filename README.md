# jconf

Package is used to load config from json files. Path to config can lead either
to directory with a bunch of json files, or to a single json file. Contents is
parsed and stored into config object, allowing attribute-based access to 
different options.

[![Build Status](https://travis-ci.com/aleosd/confj.svg?branch=master)](https://travis-ci.com/aleosd/confj)

## Installation

Package can be installed with pip:

```bash
pip install confj
```

## Usage

Usage of this utility is very simple: import `Config` class and load your config
with `load` method. Path to configs might be set via environment variable
`JSON_CONFIG_PATH` or passed directly to the `load` call:

```python
from confj import Config


config = Config()
config.load('/path/to/config')
```

If path to config is a directory, each file will be available as an attribute
of `config` object. Otherwise, if path is a file, `config` object will store
parsed json from given file, allowing access to first-level json-data via
attributes.

Config can be loaded during initialization step, just set `autoload` parameter
to `True`. Optionally path to load configs from might be passed during
initialization.

```python
from confj import Config


config = Config(default_config_path='/path/to/config', autoload=True)
```

### Config search precedence

If you directly call `load` method with `config_path` passed as parameter, then
this path is used. If no `config_path` provided or `autoload` option was used,
then `default_config_path` from initialization step is used. The last option is
to set `JSON_CONFIG_PATH` environment value. If the search is failed on all
three steps, then `ConfigException` is raised.
