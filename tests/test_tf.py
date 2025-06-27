from unittest import TestCase

import ddlcloud_tf_base_schemas


class TestCli(TestCase):
    def test_schemas(self):
        ddlcloud_tf_base_schemas.TFSet(configs={}, module_id="module", version="1.0")
