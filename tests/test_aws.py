import os

import boto3
import pytest
from moto import mock_secretsmanager

from confj import Config


@pytest.fixture()
def sm_stub():
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
    with mock_secretsmanager():
        sm_client = boto3.client("secretsmanager")
        sm_client.create_secret(
            Name="my_secret",
            SecretString='{"key": "value"}',
        )
        yield sm_client
    os.environ["AWS_DEFAULT_REGION"] = ""


def test_load_aws_secrets_manager(sm_stub):
    config = Config()
    config.load_from_aws_sm("my_secret")
    assert config.key == "value"
