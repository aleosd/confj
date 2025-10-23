import typing as t

try:
    from jsonschema import Draft7Validator
    from jsonschema.validators import extend
except ImportError:
    raise ImportError(
        'Cannot find "jsonschema" package. Either install it manually '
        "with pip, or install confj with validation option: "
        "pip install confj[validation]"
    )

from confj.confdata import ConfigData


# pylint: disable=W0613
def is_config(checker, instance: t.Any) -> bool:
    return Draft7Validator.TYPE_CHECKER.is_type(
        instance, "object"
    ) or isinstance(instance, ConfigData)


TYPE_CHECKER = Draft7Validator.TYPE_CHECKER.redefine("object", is_config)

ConfigValidator: type[Draft7Validator] = extend(
    Draft7Validator, type_checker=TYPE_CHECKER
)
config_validator = ConfigValidator(schema={"type": "object"})
