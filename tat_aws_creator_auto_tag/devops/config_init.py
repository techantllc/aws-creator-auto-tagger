# -*- coding: utf-8 -*-

import os
import json
from tat_aws_creator_auto_tag.devops.config import Config

config = Config()
if config.is_aws_lambda_runtime():
    config.update_from_env_var(prefix=config.LAMBDA_ENV_VAR_PREFIX.get_value())
else:
    config.update_from_raw_json_file()
    with open(os.path.join(config.CONFIG_DIR, "00-config-shared.json"), "rb") as f:
        config.update(json.loads(f.read().decode("utf-8")))
    config.dump_python_json_config_file()
