# -*- coding: utf-8 -*-

import boto3
from .devops.config_init import config

boto_ses = boto3.Session(profile_name=config.AWS_PROFILE_FOR_BOTO3.get_value())
