# -*- coding: utf-8 -*-

import pytest
from pytest import raises, approx
import boto3
from tat_aws_creator_auto_tag.tests import s3_client
from tat_aws_creator_auto_tag.events import EventName


class TestEventName(object):
    class TestIAM(object):
        create_event_record = {
            "eventVersion": "1.05",
            "userIdentity": {
                "type": "IAMUser",
                "principalId": "AAAAAAAAAAAAAAAAAAAAA",
                "arn": "arn:aws:iam::111122223333:user/admin",
                "accountId": "111122223333",
                "accessKeyId": "AAAAAAAAAAAAAAAAAAAAA",
                "userName": "admin",
                "sessionContext": {
                    "attributes": {
                        "mfaAuthenticated": "false",
                        "creationDate": "2019-10-26T16:29:56Z"
                    }
                },
                "invokedBy": "signin.amazonaws.com"
            },
            "eventTime": "2019-10-26T22:08:50Z",
            "eventSource": "s3.amazonaws.com",
            "eventName": "CreateBucket",
            "awsRegion": "us-east-1",
            "sourceIPAddress": "111.111.111.111",
            "userAgent": "signin.amazonaws.com",
            "requestParameters": {
                "host": [
                    "s3.amazonaws.com"
                ],
                "bucketName": "tech-ant-test-bucket-delete-soon"
            },
            "responseElements": None,
            "requestID": "EFF125F84AA162AA",
            "eventID": "aaaaaaaa-1111-1111-1111-aaaaaaaaaaaa",
            "eventType": "AwsApiCall",
            "recipientAccountId": "111122223333",
            "additionalEventData": {
                "SignatureVersion": "SigV4",
                "CipherSuite": "ECDHE-RSA-AES128-SHA",
                "AuthenticationMethod": "AuthHeader",
                "vpcEndpointId": "vpce-12345678"
            },
            "vpcEndpointId": "vpce-12345678"
        }

        def test_get_bucket_name(self):
            return EventName.S3.Bucket.get_bucket_name(self.create_event_record) \
                   == "tech-ant-test-bucket-delete-soon"

        def test_tag_it(self):
            EventName.S3.Bucket.tag_it(self.create_event_record, s3_client)


if __name__ == "__main__":
    import os

    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
