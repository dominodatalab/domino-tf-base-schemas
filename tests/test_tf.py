import json
from unittest import TestCase

from pydantic import Field

import domino_tf_base_schemas

tfset_results = {
    "first": {
        "//": "ddlcloud: {'module': 'test_tf_config'}",
        "module": {"source": "some-module-addr"},
        "locals": ["some-locals"],
        "output": {
            "schema_sensitive_output": {
                "sensitive": True,
                "value": "schema_sensitive",
            },
            "some_output": {"value": "output"},
            "sensitive_output": {"value": "sensitive output"},
        },
        "data": ["some-data"],
        "resource": {"test": "blah"},
        "terraform": {
            "backend": {"s3": {"bucket": "some-bucket", "key": "first", "region": "some-region", "encrypt": True}}
        },
    },
    "second": {
        "//": "ddlcloud: {'module': 'test_tf_config'}",
        "module": {"source": "some-module-addr"},
        "output": {
            "schema_sensitive_output": {
                "sensitive": True,
                "value": "schema_sensitive",
            },
            "some_output": {"value": "output"},
            "sensitive_output": {"value": "sensitive output"},
        },
        "resource": {"test": "blah"},
        "terraform": {
            "backend": {
                "s3": {
                    "path": "/tmp/terraform.tfstate",
                    "workspace_dir": "/tmp/",
                }
            }
        },
    },
}

output = {
    "schema_sensitive_output": {"sensitive": True, "value": "schema_sensitive"},
    "sensitive_output": {"sensitive": True, "value": "sensitive output"},
    "some_output": {"value": "output"},
}


class _TestModule(domino_tf_base_schemas.ValidatingBaseModel):
    source: str = "some-module-addr"


class _TestTFOutput(domino_tf_base_schemas.BaseTFOutput):
    some_output: str = "output"
    sensitive_output: str = "sensitive output"
    schema_sensitive_output: str = Field(json_schema_extra={"sensitive": True}, default="schema_sensitive")


class _TestTFConfig(domino_tf_base_schemas.BaseTFConfig):
    name: str = "test_tf_config"
    output: _TestTFOutput = _TestTFOutput()
    module: _TestModule = _TestModule()
    resource: dict = {"test": "blah"}


class TestCli(TestCase):
    maxDiff = None

    def test_schemas(self):
        tfset = domino_tf_base_schemas.TFSet(
            configs={
                "first": _TestTFConfig(
                    backend=domino_tf_base_schemas.TFBackendConfig(
                        type="s3",
                        config=domino_tf_base_schemas.TFS3Backend(
                            bucket="some-bucket",
                            key="first",
                            region="some-region",
                            encrypt=True,
                        ),
                    ),
                    data=["some-data"],
                    locals_=["some-locals"],
                ),
                "second": _TestTFConfig(
                    backend=domino_tf_base_schemas.TFBackendConfig(
                        type="s3",
                        config=domino_tf_base_schemas.TFLocalBackend(
                            path="/tmp/terraform.tfstate",
                            workspace_dir="/tmp/",
                        ),
                    ),
                    depends_on=["first"],
                    remote_module_refs=["first"],
                ),
            },
            module_id="module",
            version="1.0",
        )
        for phase in ["first", "second"]:
            self.assertEqual(json.loads(tfset.configs[phase].render_to_json()), tfset_results[phase])
            self.assertEqual(tfset.configs[phase].output.as_config(sensitive_fields=["sensitive_output"]), output)
