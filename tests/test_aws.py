import datetime
import os
from unittest.mock import patch

import boto3
from botocore.stub import Stubber, ANY
import pytest

from confj import Config


@pytest.fixture()
def sm_stub():
    if os.getenv("AWS_DEFAULT_REGION") is None:
        os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
    sm_client = boto3.client("secretsmanager")
    sm_stub = Stubber(sm_client)
    with patch.object(boto3, "client", return_value=sm_client):
        yield sm_stub
    sm_stub.assert_no_pending_responses()


def test_load_aws_secrets_manager(sm_stub):
    response = {
        'ARN': 'arn:aws:secretsmanager:us-east-1:88897673:my-secret',
        'Name': 'string',
        'VersionId': '3/L4kqtJlcpXroDTDmJ+rmSpXd3dIbrHY+MTRCxf3vjVBH40Nr8X8gdR'
                     'QBpUMLUo',
        'SecretBinary': b'bytes',
        'SecretString': '{"key": "value"}',
        'VersionStages': [
            'string',
        ],
        'CreatedDate': datetime.datetime.now()
    }
    expected_params = {"SecretId": ANY}
    sm_stub.add_response("get_secret_value", response, expected_params)
    with sm_stub:
        config = Config()
        config.load_from_aws_sm("my_secret")
    assert config.key == "value"
