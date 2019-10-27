# -*- coding: utf-8 -*-

import boto3

aws_profile = "tat_sanhe"

boto_ses = boto3.Session(profile_name=aws_profile)

iam_client = boto_ses.client("iam")
s3_client = boto_ses.client("s3")
