import os
from typing import Any

from aws_cdk import aws_dynamodb as dynamodb
from aws_cdk import core as cdk
from aws_cdk.aws_dynamodb import Table
from chalice.cdk import Chalice

RUNTIME_SOURCE_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), os.pardir
)


class ChaliceApp(cdk.Stack):
    def __init__(self, scope: Any, id: Any, **kwargs: Any):
        super().__init__(scope, id, **kwargs)
        self.links_table = self._create_ddb_table("links_table", "link")
        self.codes_table = self._create_ddb_table("codes_table", "code")
        self.chalice = Chalice(
            self,
            "ChaliceApp",
            source_dir=RUNTIME_SOURCE_DIR,
            stage_config={
                "environment_variables": {
                    "LINKS_TABLE": self.links_table.table_name,
                    "CODES_TABLE": self.codes_table.table_name,
                },
                "api_gateway_stage": "l",
            },
        )
        self.links_table.grant_read_write_data(
            self.chalice.get_role("DefaultRole")
        )
        self.codes_table.grant_read_write_data(
            self.chalice.get_role("DefaultRole")
        )

    def _create_ddb_table(self, name: str, partition_key_name: str) -> Table:
        dynamodb_table = dynamodb.Table(
            self,
            name,
            partition_key=dynamodb.Attribute(
                name=partition_key_name, type=dynamodb.AttributeType.STRING
            ),
            removal_policy=cdk.RemovalPolicy.DESTROY,
        )
        return dynamodb_table
