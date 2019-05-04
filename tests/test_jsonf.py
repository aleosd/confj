import os
import pathlib

import pytest

from confj import Config
from confj import const
from confj.exceptions import NoConfigOptionError, ConfigException


def get_dir_conf():
    path = pathlib.Path(__file__).parent / 'fixtures' / 'valid_conf'
    config = Config()
    config.load(path)
    return config


def get_file_conf():
    path = pathlib.Path(__file__).parent / 'fixtures' / 'valid_conf' / \
           'settings.json'
    config = Config()
    config.load(path)
    return config


conf_params = [get_dir_conf().settings, get_file_conf()]


@pytest.fixture()
def dir_config():
    return get_dir_conf()


@pytest.fixture()
def file_config():
    return get_file_conf()


def test_config_dir_load(dir_config):
    assert list(dir_config.c_keys()) == [
        'empty', 'projects', 'secrets', 'settings']
    assert list(dir_config.secrets.c_keys()) == ['password', 'user']


def test_config_file_load(file_config):
    assert list(file_config.c_keys()) == [
        'array_of_objects', 'some_array',
        'some_bool', 'some_int', 'some_nested_dict', 'some_none', 'some_string'
    ]


def test_config_access(dir_config):
    assert dir_config.secrets.user == 'username'
    assert dir_config['secrets'].user == 'username'
    assert dir_config['secrets']['user'] == 'username'
    assert dir_config.secrets['user'] == 'username'
    assert dir_config.secrets.get('user') == 'username'
    assert dir_config.secrets.get('token') is None
    assert dir_config.secrets.get('token', 'abc') == 'abc'

    with pytest.raises(NoConfigOptionError):
        _ = dir_config.some_wrong_option
        _ = dir_config.settings.some_wrong_option
        _ = dir_config.settings.some_wrong_option.even_deeper
        _ = dir_config.settings.some_wrong_option.get('foo')
        _ = dir_config['some_wrong_option']
        _ = dir_config.settings['some_wrong_option']
        _ = dir_config.settings['some_wrong_option'].even_deeper
        _ = dir_config.settings['some_wrong_option'].get('foo')


@pytest.mark.parametrize('config', conf_params)
def test_data_types(config):
    assert config.some_int == 13
    assert config.some_bool is True
    assert config.some_none is None
    assert config.some_string == "string_value"
    assert config.some_array == [13, "string", False]
    assert config.some_nested_dict == {
        "port": 5432,
        "host": "localhost"
    }
    for i, obj in enumerate(config.array_of_objects):
        idx = i + 1
        assert obj == {"id": idx, "name": "obj{}".format(idx)}


@pytest.mark.parametrize('config', conf_params)
def test_items_access(config):
    for option, value in config.c_items():
        if option == 'some_int':
            assert value == 13
        if option == 'some_bool':
            assert value is True
        if option == 'some_none':
            assert value is None
        if option == 'some_string':
            assert value == "string_value"
        if option == 'some_array':
            assert value == [13, "string", False]
        if option == 'some_nested_dict':
            assert value == {
                "port": 5432,
                "host": "localhost"
            }
        if option == 'array_of_objects':
            for i, obj in enumerate(value):
                idx = i + 1
                assert obj == {"id": idx, "name": "obj{}".format(idx)}


def test_select_config_path():
    config = Config(default_config_path='./fixtures')
    assert config._select_config_path() == './fixtures'

    config = Config()
    assert config._select_config_path('param_path') == 'param_path'

    os.environ[const.ENV_CONF_PATH_NAME] = 'env_config_path'
    config = Config()
    assert config._select_config_path() == 'env_config_path'
    del os.environ[const.ENV_CONF_PATH_NAME]

    config = Config()
    with pytest.raises(ConfigException):
        config._select_config_path()


def test_autoload():
    path = str(pathlib.Path(__file__).parent / 'fixtures' / 'valid_conf')
    config = Config(default_config_path=path, autoload=True)
    assert list(config.c_keys()) == ['empty', 'projects', 'secrets', 'settings']


def test_empty(dir_config):
    assert dir_config.empty == ''


def test_config_data(dir_config):
    assert dir_config.secrets.c_data() == {
        'user': 'username',
        'password': 'password',
    }
    assert dir_config.projects.c_data() == [{
      "name": "Project1",
      "id": 1,
      "data": {
        "key1": "value1",
        "key2": "value2"
      }
    }, {
      "name": "Project2",
      "id": 2,
      "data": {
        "key1": "value1",
        "key2": "value2"
      }
    }, {
      "name": "Project3",
      "id": 3,
      "data": {
        "key1": "value1",
        "key2": "value2"
      }
    }]


def test_config_format(dir_config):
    assert dir_config.secrets.c_format() == "{'password': 'password', " \
                                            "'user': 'username'}"
    settings_pformat = """{ 'array_of_objects': [ {'id': 1, 'name': 'obj1'},
                        {'id': 2, 'name': 'obj2'},
                        {'id': 3, 'name': 'obj3'}],
  'some_array': [13, 'string', False],
  'some_bool': True,
  'some_int': 13,
  'some_nested_dict': {'host': 'localhost', 'port': 5432},
  'some_none': None,
  'some_string': 'string_value'}"""
    assert dir_config.settings.c_format() == settings_pformat
