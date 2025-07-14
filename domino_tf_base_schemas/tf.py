import json
from typing import Union

from pydantic import BaseModel, Field


class ValidatingBaseModel(BaseModel, validate_assignment=True, strict=True):
    pass


class BaseTFOutput(ValidatingBaseModel):
    def as_config(self, sensitive_fields: list[str] | None = None) -> dict:
        output = {k: {"value": v} for k, v in self.model_dump().items()}

        for k, v in self.__class__.model_fields.items():
            if v.json_schema_extra and v.json_schema_extra["sensitive"]:  # type: ignore
                output[k]["sensitive"] = True

        # Allows to conditionally(dynamic) set `sensitive` outputs
        if sensitive_fields is not None:
            for k in sensitive_fields:
                if k in output:
                    output[k]["sensitive"] = True

        return output


class TFSet(ValidatingBaseModel):
    configs: dict
    module_id: str
    version: str


class TFLocalBackend(ValidatingBaseModel):
    path: str
    workspace_dir: str | None = None


# TODO: Work out all the vars/scenarios
class TFS3Backend(ValidatingBaseModel):
    bucket: str
    key: str
    region: str
    encrypt: bool = True
    # use_lockfile: bool = True  # TODO: no workie


class TFBackendConfig(ValidatingBaseModel):
    type_: str = Field(alias="type")
    config: Union[TFLocalBackend, TFS3Backend]


class BaseTFConfig(ValidatingBaseModel):
    remote_module_refs: list[str] | None = None
    data: list | None = None
    depends_on: list[str] | None = None
    locals_: list | None = None
    backend: TFBackendConfig | None = None

    def render_to_json(self) -> str:
        name = getattr(self, "name")
        struct: dict = {"//": f"ddlcloud: {{'module': '{name}'}}"}

        if module := getattr(self, "module", None):
            struct["module"] = module.model_dump(by_alias=True, exclude_none=True)

        if getattr(self, "resource", None):
            struct["resource"] = self.model_dump(by_alias=True, exclude_none=True)["resource"]

        if output := getattr(self, "output", None):
            struct["output"] = output.as_config()

        if data := getattr(self, "data", None):
            struct["data"] = data

        if locals_ := getattr(self, "locals_", None):
            struct["locals"] = locals_

        backend = getattr(self, "backend")
        struct["terraform"] = {
            "backend": {
                backend.type_: backend.config.model_dump(by_alias=True),
            }
        }

        return json.dumps(struct, indent=4)
