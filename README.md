# ConfJ

Package is used to load config from json files. Path to config can lead either
to directory with a bunch of json files, or to a single json file. Contents is
parsed and stored into config object, allowing attribute-based access to 
different options.

[![Build Status](https://travis-ci.com/aleosd/confj.svg?branch=master)](https://travis-ci.com/aleosd/confj)
[![Say Thanks!](https://img.shields.io/badge/Say%20Thanks-!-1EAEDB.svg)](https://saythanks.io/to/aleosd)

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
parsed json from given file, allowing access to data via attributes.

Config can be loaded during initialization step, just set `autoload` parameter
to `True`. Optionally path to load configs from might be passed during
initialization.

```python
from confj import Config


config = Config(default_config_path='/path/to/config', autoload=True)
```

After config is loaded, it's options are accessible via attributes of `config`
object, ot `dict`-like syntax:

```python
>>> config.username
'user'

>>> config['username']
'user'

>>> config.get('username')
'user'

``` 

### Config search precedence

1. If you directly call `load` method with `config_path` passed as parameter,
then this path is used.
2. If no `config_path` provided or `autoload` option was used,
then `default_config_path` from initialization step is used.
3. The last option is to set `JSON_CONFIG_PATH` environment value. If the search
is failed on all three steps, then `ConfigException` is raised.

### Available methods

All `config` object's method names are starting with `c_`, to avoid possible
clash with possible config options

* `c_format` returns pretty formatted sting representing config;
* `c_pprint` outputs formatted config to stdout;
* `c_validate` validates config against given json schema. See `Validation`
section below.

### Validation

Config must be a valid json object, so we can validate it against provided
json schema. To use config validation `jsonschema` package must be installed.
It might be done as a separate step as

```bash
pip install jsonschema
```

or during `confj` installation time:

```bash
pip install confj[validation]
```

Then config validation can be done with `c_validate` method:

```python
from confj import Config

config = Config(default_config_path='/path/to/config', autoload=True)
schema = {"type": "object"}
is_valid = config.c_validate(schema)
```

By default `c_validate` will return either `True` of `False`. To see actual
validation error just pass `do_raise=True` as additional parameter, and catch
`ValidationError` later:

```python
from confj import Config
from jsonschema import ValidationError

config = Config(default_config_path='/path/to/config', autoload=True)
schema = {"type": "object"}

try:
    config.c_validate(schema, do_raise=True)
except ValidationError as err:
    print(f'Looks like config is invalid: {err}')
```

To read more on json validation one can at
[json-schema.org](https://json-schema.org/understanding-json-schema/index.html)
