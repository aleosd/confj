import json
import os
import pathlib

from jsonschema import ValidationError
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
    assert list(dir_config.keys()) == [
        'empty', 'projects', 'secrets', 'settings']
    assert list(dir_config.secrets.keys()) == ['password', 'user']


def test_config_file_load(file_config):
    assert list(file_config.keys()) == [
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
    assert dir_config.settings.some_nested_dict.port == 5432

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
    for option, value in config.items():
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
    assert list(config.keys()) == ['empty', 'projects', 'secrets', 'settings']


def test_empty(dir_config):
    assert dir_config.empty == dict()


def test_config_data(dir_config):
    assert dir_config.secrets == {
        'user': 'username',
        'password': 'password',
    }
    assert dir_config.projects == [{
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


@pytest.mark.parametrize('schema,do_raise,result', [
    ({}, False, True),
    (True, False, True),
    ({
         "type": "object",
         "properties": {
             "some_int": {"type": "integer"},
             "some_bool": {"type": "boolean"},
             "some_string": {"type": "string"},
             "some_array": {"type": "array"},
             "some_none": {"type": "null"},
             "some_nested_dict": {"type": "object"},
             "some_array_of_objects": {
                 "type": "array", "items": {"type": "object"}
             },
         }
     }, False, True),
    ({
         "type": "object",
         "properties": {
             "some_int": {"type": "string"},
             "some_bool": {"type": "boolean"},
             "some_string": {"type": "string"},
         }
     }, False, False),
    ({
         "type": "object",
         "properties": {
             "some_int": {"type": "string"},
             "some_bool": {"type": "boolean"},
             "some_string": {"type": "string"},
         }
     }, True, False),
    (False, False, False),
    (False, True, False),
])
def test_validation(file_config, schema, do_raise, result):
    if do_raise:
        with pytest.raises(ValidationError):
            file_config.c_validate(schema, do_raise=True)
    else:
        assert file_config.c_validate(schema) is result


def test_value_unpacking(file_config, dir_config):
    for c in [file_config, dir_config]:
        assert dict(**c) == c


def test_keys(dir_config):
    assert dir_config.keys()
    assert dir_config.settings.keys()

    with pytest.raises(AttributeError):
        _ = dir_config.projects.keys()


def test_iteration(dir_config):
    expected_keys = ['empty', 'projects', 'secrets', 'settings']
    for actual, expected in zip(dir_config, expected_keys):
        assert actual == expected


def test_hash(dir_config):
    hash(dir_config)
    for config_item in dir_config.keys():
        hash(dir_config[config_item])


def test_config_set(dir_config):
    dir_config.set('new_key', 'new_value')
    assert dir_config.new_key == 'new_value'

    dir_config.set('array_key', ['a', 'b', 'c'])
    assert dir_config.array_key == ['a', 'b', 'c']

    dir_config.secrets.set('expire_days', 5)
    assert dir_config.secrets.expire_days == 5

    dir_config.empty.set('data', {'days': 5, 'weeks': 3, 't': {'n': 'n'}})
    assert dir_config.empty.data == {'days': 5, 'weeks': 3, 't': {'n': 'n'}}
    assert dir_config.empty.data.days == 5
    assert dir_config.empty.data.t.n == 'n'

    dir_config.settings.some_nested_dict.set('dbname', 'test')
    assert dir_config.settings.some_nested_dict.dbname == 'test'

    with pytest.raises(ConfigException):
        dir_config.projects.set('new_item', {'a': 'b'})


def test_load_from_obj():
    file_path = pathlib.Path(__file__).parent / 'fixtures' / 'valid_conf' / \
           'settings.json'
    python_obj = json.loads(file_path.read_text())
    assert isinstance(python_obj, dict)
    config = Config()
    config.load_from_obj(python_obj)

    assert config.some_int == 13
    assert config.some_bool is True
    assert config.some_string == 'string_value'
    assert config.some_array == [13, "string", False]
    assert config.some_none is None
    assert config.some_nested_dict == {'port': 5432, 'host': 'localhost'}
    assert config.some_nested_dict.port == 5432
    assert config.some_nested_dict.host == 'localhost'
    assert config.array_of_objects == [
        {"id": 1, "name": "obj1"},
        {"id": 2, "name": "obj2"},
        {"id": 3, "name": "obj3"}
    ]
