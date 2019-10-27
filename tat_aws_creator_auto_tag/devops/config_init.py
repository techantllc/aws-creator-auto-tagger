# -*- coding: utf-8 -*-

from .config import Config

config = Config()
if config.is_aws_lambda_runtime():
    pass
else:
    config.update_from_raw_json_file()
