# -*- coding: utf-8 -*-

import gzip
import json
from tat_aws_creator_auto_tag.boto_ses import boto_ses
from tat_aws_creator_auto_tag.events import EventName, RecordParser, ResourceNotSupportedError
from tat_aws_creator_auto_tag.logger import logger

s3_client = boto_ses.client("s3")


def handler(event, context):
    bucket_name = event["Records"][0]["s3"]["bucket"]["name"]
    object_key = event["Records"][0]["s3"]["object"]["key"]

    res_get_object = s3_client.get_object(
        Bucket=bucket_name, Key=object_key
    )
    content = res_get_object["Body"].read()
    cloudtrail_data = json.loads(gzip.decompress(content).decode("utf-8"))
    for record in cloudtrail_data["Records"]:
        if RecordParser.is_create_event(record):
            try:
                EventName.tag_it(record, boto_ses, verbose=True)
            except ResourceNotSupportedError as _:
                pass
