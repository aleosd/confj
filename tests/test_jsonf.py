import pathlib

import pytest

from confj import Config
from confj.exceptions import NoConfigOptionError


def get_dir_conf():
    path = pathlib.Path(__file__).parent / 'fixtures'
    config = Config()
    config.load(path)
    return config


def get_file_conf():
    path = pathlib.Path(__file__).parent / 'fixtures' / 'settings.json'
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
    assert list(dir_config.c_keys()) == ['projects', 'secrets', 'settings']
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
